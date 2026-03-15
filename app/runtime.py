import gc
import socket
import time
import ntptime

from machine import I2C, Pin, RTC

from wlan import set_wlan
from config import APP, EXPORTS, SENSORS
from sensors import (
    AHT20Sensor,
    BME680Sensor,
    BME280Sensor,
    DHT22Sensor,
    RainGaugeSensor,
    SensorManager,
    WindDirectionSensor,
    WindSpeedSensor,
)
from app.display import Display
from app.exporters import (
    ExportManager,
    LoRaWanExporter,
    MqttExporter,
    SerialExporter,
    UdpExporter,
)
from app.stats_buffer import CircularStatsBuffer
from app.web import render_html


def _bcd_to_dec(value):
    return ((value >> 4) * 10) + (value & 0x0F)


def _dec_to_bcd(value):
    return ((value // 10) << 4) | (value % 10)


def _open_i2c_from_cfg(i2c_cfg):
    return I2C(
        i2c_cfg["id"],
        sda=Pin(i2c_cfg["sda_pin"]),
        scl=Pin(i2c_cfg["scl_pin"]),
        freq=i2c_cfg["freq"],
    )


def _read_ds3231_datetime(i2c, address):
    raw = i2c.readfrom_mem(address, 0x00, 7)
    second = _bcd_to_dec(raw[0] & 0x7F)
    minute = _bcd_to_dec(raw[1] & 0x7F)
    hour = _bcd_to_dec(raw[2] & 0x3F)
    weekday = (_bcd_to_dec(raw[3] & 0x07) - 1) % 7
    day = _bcd_to_dec(raw[4] & 0x3F)
    month = _bcd_to_dec(raw[5] & 0x1F)
    year = 2000 + _bcd_to_dec(raw[6])
    return (year, month, day, weekday, hour, minute, second, 0)


def _write_ds3231_datetime(i2c, address, dt):
    year, month, day, weekday, hour, minute, second, _ = dt
    payload = bytes(
        [
            _dec_to_bcd(second),
            _dec_to_bcd(minute),
            _dec_to_bcd(hour),
            _dec_to_bcd((weekday % 7) + 1),
            _dec_to_bcd(day),
            _dec_to_bcd(month),
            _dec_to_bcd(year % 100),
        ]
    )
    i2c.writeto_mem(address, 0x00, payload)


def _is_datetime_valid(min_year):
    year = time.localtime()[0]
    return year >= min_year


def _load_rtc_from_ds3231(i2c_cfg, rtc_cfg, min_year):
    if not rtc_cfg.get("enabled", False):
        return False
    try:
        i2c = _open_i2c_from_cfg(i2c_cfg)
        dt = _read_ds3231_datetime(i2c, rtc_cfg.get("address", 0x68))
        RTC().datetime(dt)
        return _is_datetime_valid(min_year)
    except Exception as exc:
        print("RTC load skipped:", exc)
        return False


def _save_rtc_to_ds3231(i2c_cfg, rtc_cfg):
    if not rtc_cfg.get("enabled", False):
        return False
    try:
        i2c = _open_i2c_from_cfg(i2c_cfg)
        _write_ds3231_datetime(i2c, rtc_cfg.get("address", 0x68), RTC().datetime())
        return True
    except Exception as exc:
        print("RTC save skipped:", exc)
        return False


def _resolve_ntp_mode(app_cfg):
    mode = app_cfg.get("ntp_sync_mode")
    if mode:
        return str(mode).lower()
    # Backward compatibility with legacy `use_ntp` setting.
    return "always" if app_cfg.get("use_ntp", False) else "never"


def _is_ntp_pin_requested(app_cfg):
    pin_no = app_cfg.get("ntp_trigger_pin")
    if pin_no is None:
        return False

    pull = app_cfg.get("ntp_trigger_pull", "up")
    pin_pull = None
    if pull == "up":
        pin_pull = Pin.PULL_UP
    elif pull == "down":
        pin_pull = Pin.PULL_DOWN

    if pin_pull is None:
        pin = Pin(pin_no, Pin.IN)
    else:
        pin = Pin(pin_no, Pin.IN, pin_pull)
    is_high = pin.value() == 1
    active_high = app_cfg.get("ntp_trigger_active_high", True)
    return is_high if active_high else not is_high


def _should_sync_ntp(app_cfg, rtc_valid):
    mode = _resolve_ntp_mode(app_cfg)
    if mode == "never":
        return False
    if mode == "always":
        return True
    if mode == "auto":
        return not rtc_valid
    if mode == "pin":
        return _is_ntp_pin_requested(app_cfg)
    # Safe fallback: do not sync if mode is unknown.
    return False


def _build_sensor_manager():
    i2c_cfg = SENSORS["i2c"]
    display_cfg = SENSORS.get("display", {})
    sensor_list = []

    bme = None
    bme_cfg = SENSORS["bme680"]
    if bme_cfg["enabled"]:
        bme = BME680Sensor(
            i2c_id=i2c_cfg["id"],
            sda_pin=i2c_cfg["sda_pin"],
            scl_pin=i2c_cfg["scl_pin"],
            i2c_freq=i2c_cfg["freq"],
            address=bme_cfg.get("address"),
            temp_offset_c=bme_cfg["temp_offset_c"],
            humidity_offset_pct=bme_cfg["humidity_offset_pct"],
            pressure_offset_hpa=bme_cfg["pressure_offset_hpa"],
        )
        sensor_list.append(bme)

    i2c_aux_cfg = SENSORS.get("i2c_aux", i2c_cfg)

    bme280_cfg = SENSORS.get("bme280", {})
    if bme280_cfg.get("enabled", False):
        sensor_list.append(
            BME280Sensor(
                i2c_id=i2c_aux_cfg["id"],
                sda_pin=i2c_aux_cfg["sda_pin"],
                scl_pin=i2c_aux_cfg["scl_pin"],
                i2c_freq=i2c_aux_cfg["freq"],
                address=bme280_cfg.get("address", 0x77),
            )
        )

    aht20_cfg = SENSORS.get("aht20", {})
    if aht20_cfg.get("enabled", False):
        sensor_list.append(
            AHT20Sensor(
                i2c_id=i2c_aux_cfg["id"],
                sda_pin=i2c_aux_cfg["sda_pin"],
                scl_pin=i2c_aux_cfg["scl_pin"],
                i2c_freq=i2c_aux_cfg["freq"],
            )
        )

    dht22_cfg = SENSORS.get("dht22", {})
    if dht22_cfg.get("enabled", False):
        sensor_list.append(
            DHT22Sensor(
                pin=dht22_cfg.get("pin", 13),
                min_interval_ms=dht22_cfg.get("min_interval_ms", 2000),
            )
        )

    ws_cfg = SENSORS["wind_speed"]
    if ws_cfg["enabled"]:
        sensor_list.append(
            WindSpeedSensor(
                pin=ws_cfg["pin"],
                pull_up=ws_cfg["pull_up"],
                kmh_per_hz=ws_cfg["kmh_per_hz"],
            )
        )

    wd_cfg = SENSORS["wind_dir"]
    if wd_cfg["enabled"]:
        sensor_list.append(WindDirectionSensor(adc_pin=wd_cfg["adc_pin"]))

    rg_cfg = SENSORS["rain_gauge"]
    if rg_cfg["enabled"]:
        sensor_list.append(
            RainGaugeSensor(
                pin=rg_cfg["pin"],
                pull_up=rg_cfg["pull_up"],
                mm_per_tip=rg_cfg["mm_per_tip"],
            )
        )

    i2c_for_display = None
    display_addr = display_cfg.get("addr")
    if display_cfg.get("enabled", True):
        if display_cfg.get("share_sensor_i2c", False):
            i2c_for_display = bme.i2c if bme else None
        else:
            i2c_for_display = I2C(
                display_cfg.get("id", i2c_cfg["id"]),
                sda=Pin(display_cfg.get("sda_pin", i2c_cfg["sda_pin"])),
                scl=Pin(display_cfg.get("scl_pin", i2c_cfg["scl_pin"])),
                freq=display_cfg.get("freq", i2c_cfg["freq"]),
            )
    return SensorManager(sensor_list), i2c_for_display, display_addr


def _send_html(conn, html):
    body = html.encode("utf-8")
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "Cache-Control: no-store\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(len(body))
    conn.sendall(headers.encode("utf-8"))
    conn.sendall(body)


def _send_redirect(conn, location="/"):
    headers = (
        "HTTP/1.1 303 See Other\r\n"
        "Location: {}\r\n"
        "Cache-Control: no-store\r\n"
        "Content-Length: 0\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(location)
    conn.sendall(headers.encode("utf-8"))


def _path_only(path):
    if not path:
        return "/"
    return path.split("?", 1)[0]


def _parse_http_path(request_bytes):
    try:
        request_line = request_bytes.decode().split("\r\n", 1)[0]
        parts = request_line.split(" ")
        if len(parts) >= 2:
            return parts[1]
    except Exception:
        pass
    return "/"


def _manual_ntp_sync(i2c_cfg, rtc_cfg):
    try:
        ntptime.settime()
        _save_rtc_to_ds3231(i2c_cfg, rtc_cfg)
        ts = time.localtime()
        return "NTP sync OK {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            ts[0], ts[1], ts[2], ts[3], ts[4], ts[5]
        )
    except Exception as exc:
        return "NTP sync failed: {}".format(exc)


def _print_export_modes(mqtt_cfg, serial_cfg, udp_cfg, lorawan_cfg):
    print("Transmission modes:")
    if mqtt_cfg.get("enabled", False):
        topic = mqtt_cfg.get("topic", "weather/sensors")
        print(
            " - MQTT: ON -> {}:{} raw_topic={} every {} s | aggregated_topic={} every {} s".format(
                mqtt_cfg.get("broker"),
                mqtt_cfg.get("port", 1883),
                _mqtt_raw_topic(topic),
                APP.get("acquisition_interval_seconds", APP.get("web_refresh_seconds", 8)),
                topic,
                APP.get("aggregation_interval_seconds", 300),
            )
        )
    else:
        print(" - MQTT: OFF")

    if udp_cfg.get("enabled", False):
        print(
            " - UDP: ON -> {}:{} raw every {} s | aggregated every {} s".format(
                udp_cfg.get("host"),
                udp_cfg.get("port", 9999),
                APP.get("acquisition_interval_seconds", APP.get("web_refresh_seconds", 8)),
                APP.get("aggregation_interval_seconds", 300),
            )
        )
    else:
        print(" - UDP: OFF")

    if serial_cfg.get("enabled", False):
        print(
            " - SERIAL: ON (raw_prefix={} every {} s | aggregated_prefix={} every {} s)".format(
                _serial_raw_prefix(serial_cfg.get("prefix", "JSON")),
                APP.get("acquisition_interval_seconds", APP.get("web_refresh_seconds", 8)),
                serial_cfg.get("prefix", "JSON"),
                APP.get("aggregation_interval_seconds", 300),
            )
        )
    else:
        print(" - SERIAL: OFF")

    if lorawan_cfg.get("enabled", False):
        print(
            " - LORAWAN: ON (port={} raw every {} s | aggregated every {} s)".format(
                lorawan_cfg.get("port", 1),
                APP.get("acquisition_interval_seconds", APP.get("web_refresh_seconds", 8)),
                APP.get("aggregation_interval_seconds", 300),
            )
        )
    else:
        print(" - LORAWAN: OFF")

    print("Export trigger: raw sensor snapshots and aggregated snapshots are exported separately.")


def _mqtt_raw_topic(base_topic):
    return "{}/raw".format(base_topic.rstrip("/"))


def _serial_raw_prefix(base_prefix):
    if not base_prefix:
        return "RAW"
    return "{}_RAW".format(base_prefix)


def _build_export_payload(reading, export_mode, emitted_at, interval_seconds):
    payload = dict(reading or {})
    payload["export_mode"] = export_mode
    payload["export_interval_seconds"] = int(interval_seconds)
    if payload.get("timestamp") is None:
        payload["timestamp"] = emitted_at
    return payload


def _interval_ms(seconds, default_seconds):
    if seconds is None:
        seconds = default_seconds
    try:
        seconds = float(seconds)
    except Exception:
        seconds = default_seconds
    if seconds <= 0:
        seconds = 1
    return int(seconds * 1000)


def _sensor_acquisition_interval_ms(app_cfg):
    seconds = app_cfg.get("acquisition_interval_seconds")
    if seconds is None:
        seconds = app_cfg.get("web_refresh_seconds", 8)
    return _interval_ms(seconds, 8)


def _aggregation_interval_ms(app_cfg, sensor_interval_ms):
    aggregation_ms = _interval_ms(
        app_cfg.get("aggregation_interval_seconds"),
        sensor_interval_ms / 1000,
    )
    if aggregation_ms < sensor_interval_ms:
        return sensor_interval_ms
    return aggregation_ms


def _buffer_capacity(sensor_interval_ms, aggregation_interval_ms):
    return max(1, (aggregation_interval_ms + sensor_interval_ms - 1) // sensor_interval_ms)


def _perform_acquisition(sensors, display):
    started_ms = time.ticks_ms()
    reading = sensors.read_all()
    if display:
        display.show_reading(reading)
    duration_ms = time.ticks_diff(time.ticks_ms(), started_ms)
    return reading, duration_ms


def _log_export_results(export_results, export_mode):
    for exporter_name, exporter_result in export_results.items():
        if isinstance(exporter_result, str):
            print(
                "Export error [{}:{}]: {}".format(
                    export_mode, exporter_name, exporter_result
                )
            )
        elif exporter_result:
            print("Exported {} via {}.".format(export_mode, exporter_name))


def main():
    gc.collect()
    led = Pin("LED", Pin.OUT)

    sensors, i2c, display_addr = _build_sensor_manager()
    display = None
    if i2c:
        try:
            display = Display(i2c, addr=display_addr)
        except OSError as e:
            print("OLED init skipped:", e)
    mqtt_cfg = EXPORTS["mqtt"]
    serial_cfg = EXPORTS.get("serial", {})
    udp_cfg = EXPORTS.get("udp", {})
    lorawan_cfg = EXPORTS["lorawan"]
    _print_export_modes(mqtt_cfg, serial_cfg, udp_cfg, lorawan_cfg)
    exporters = ExportManager(
        [
            MqttExporter(
                enabled=mqtt_cfg["enabled"],
                broker=mqtt_cfg["broker"],
                topic=mqtt_cfg["topic"],
                client_id=mqtt_cfg["client_id"],
                port=mqtt_cfg["port"],
                user=mqtt_cfg["user"],
                password=mqtt_cfg["password"],
                keepalive=mqtt_cfg["keepalive"],
                ssl=mqtt_cfg["ssl"],
                qos=mqtt_cfg["qos"],
                retain=mqtt_cfg["retain"],
            ),
            SerialExporter(
                enabled=serial_cfg.get("enabled", False),
                prefix=serial_cfg.get("prefix", "JSON"),
            ),
            UdpExporter(
                enabled=udp_cfg.get("enabled", False),
                host=udp_cfg.get("host"),
                port=udp_cfg.get("port", 9999),
            ),
            LoRaWanExporter(
                enabled=lorawan_cfg["enabled"],
                port=lorawan_cfg["port"],
            ),
        ]
    )

    if display:
        display.show_boot(["Initializing...", "Weather node"])
    led.value(1)

    wlan, ip = set_wlan(led)
    if display:
        display.show_boot(["Wifi OK"])

    rtc_cfg = SENSORS.get("rtc", {})
    ntp_min_year = APP.get("ntp_min_year", 2024)
    rtc_valid = _load_rtc_from_ds3231(SENSORS["i2c"], rtc_cfg, ntp_min_year)
    print("RTC valid:", rtc_valid, "year:", time.localtime()[0])
    if display and rtc_valid:
        display.show_boot(["Initializing...", "Weather node", "RTC OK"])

    ntp_required = _should_sync_ntp(APP, rtc_valid)
    print("NTP mode:", _resolve_ntp_mode(APP), "sync_required:", ntp_required)
    last_ntp_message = None
    if ntp_required:
        try:
            ntptime.settime()
            _save_rtc_to_ds3231(SENSORS["i2c"], rtc_cfg)
            ts = time.localtime()
            last_ntp_message = "NTP sync OK {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                ts[0], ts[1], ts[2], ts[3], ts[4], ts[5]
            )
            if display:
                display.show_boot(["Wifi OK", "NTP OK"])
        except Exception as exc:
            print("NTP skipped:", exc)
            if display:
                display.show_boot(["Wifi OK", "NTP skipped"])

    led.value(0)

    bind_addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass
    server.bind(bind_addr)
    server.listen(5)
    server.settimeout(1.0)
    print("HTTP server ready on http://{}".format(ip))
    print("HTTP bind address:", bind_addr)
    acquisition_interval_ms = _sensor_acquisition_interval_ms(APP)
    aggregation_interval_ms = _aggregation_interval_ms(APP, acquisition_interval_ms)
    buffer_capacity = _buffer_capacity(acquisition_interval_ms, aggregation_interval_ms)
    print("Sensor acquisition interval:", acquisition_interval_ms, "ms")
    print("Aggregation interval:", aggregation_interval_ms, "ms")
    print("Ring buffer capacity:", buffer_capacity, "samples")
    if display:
        display.show_boot(["Wifi OK", ip, "Web ready", "Auto acquire"])

    stats_buffer = CircularStatsBuffer(buffer_capacity)
    last_reading = None
    last_aggregate_reading = None
    web_reading = None
    last_acquisition_ms = time.ticks_add(time.ticks_ms(), -acquisition_interval_ms)
    aggregation_started_ms = None

    while True:
        conn = None
        try:
            if gc.mem_free() < 102000:
                gc.collect()
            if not wlan.isconnected():
                print("Wi-Fi disconnected, reconnecting...")
                wlan, ip = set_wlan(led)
                print("HTTP server still listening on http://{}".format(ip))
                if display:
                    display.show_boot(["Wifi OK", ip, "Web ready", "Auto acquire"])

            now_ms = time.ticks_ms()
            if (
                last_reading is None
                or time.ticks_diff(now_ms, last_acquisition_ms) >= acquisition_interval_ms
            ):
                last_reading, acquisition_duration_ms = _perform_acquisition(sensors, display)
                last_acquisition_ms = now_ms
                stats_buffer.add(last_reading)
                if aggregation_started_ms is None:
                    aggregation_started_ms = now_ms
                print(
                    "Acquisition updated at {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                        *time.localtime()[:6]
                    )
                )
                print("Acquisition duration:", acquisition_duration_ms, "ms")
                if acquisition_duration_ms > acquisition_interval_ms:
                    print(
                        "Acquisition overrun: cycle took longer than configured interval."
                    )
                raw_payload = _build_export_payload(
                    last_reading,
                    "raw",
                    time.time(),
                    acquisition_interval_ms // 1000,
                )
                raw_route = {
                    "topic": _mqtt_raw_topic(mqtt_cfg.get("topic", "weather/sensors")),
                    "prefix": _serial_raw_prefix(serial_cfg.get("prefix", "JSON")),
                }
                export_results = exporters.publish_due(raw_payload, route=raw_route)
                _log_export_results(export_results, "raw")
                if time.ticks_diff(now_ms, aggregation_started_ms) >= aggregation_interval_ms:
                    aggregate_reading = stats_buffer.build_snapshot(
                        window_seconds=aggregation_interval_ms // 1000,
                        closed_at=time.time(),
                    )
                    last_aggregate_reading = _build_export_payload(
                        aggregate_reading,
                        "aggregated",
                        time.time(),
                        aggregation_interval_ms // 1000,
                    )
                    web_reading = last_aggregate_reading
                    stats_buffer.reset()
                    aggregation_started_ms = now_ms
                    print(
                        "Aggregate snapshot ready with",
                        last_aggregate_reading.get("aggregation_samples", 0),
                        "samples.",
                    )
                    export_results = exporters.publish_due(last_aggregate_reading)
                    _log_export_results(export_results, "aggregated")

            conn, addr = server.accept()
            print("HTTP client connected:", addr)
            conn.settimeout(3.0)
            request = conn.recv(1024)
            print("HTTP request bytes:", len(request))
            conn.settimeout(None)
            path = _parse_http_path(request)
            route = _path_only(path)

            ntp_message = last_ntp_message
            if route == "/sync-ntp":
                last_ntp_message = _manual_ntp_sync(SENSORS["i2c"], rtc_cfg)
                print(last_ntp_message)
                _send_redirect(conn, "/")
                conn.close()
                continue

            html = render_html(
                web_reading or last_reading or {},
                refresh_seconds=APP["web_refresh_seconds"],
                ntp_message=ntp_message,
                current_dt=time.localtime(),
            )

            _send_html(conn, html)
            conn.close()
            print("HTTP request served:", addr)
        except OSError as exc:
            if conn:
                conn.close()
            if exc.args and exc.args[0] in (110, "timed out"):
                continue
            print("HTTP server OSError:", exc)
            time.sleep_ms(100)

