def _first(data, keys, default="-"):
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return default


def _to_float(value):
    try:
        return float(value)
    except Exception:
        return None


def _fmt_delta(value, ref):
    if value is None or ref is None:
        return "-"
    delta = value - ref
    return "{:+.2f}".format(delta)


def _pick_reference(sensors_data):
    for sensor in sensors_data:
        if sensor["t"] is not None or sensor["h"] is not None or sensor["p"] is not None:
            return sensor
    return None


def _render_compare_rows(data):
    sensors = [
        ("BME680", "sensor_bme680_temperature_c", "sensor_bme680_humidity_pct", "sensor_bme680_pressure_hpa"),
        ("BME280", "sensor_bme280_temperature_c", None, "sensor_bme280_pressure_hpa"),
        ("AHT20", "sensor_aht20_temperature_c", "sensor_aht20_humidity_pct", None),
        ("DHT22", "sensor_dht22_temperature_c", "sensor_dht22_humidity_pct", None),
    ]

    sensors_data = []
    for name, t_key, h_key, p_key in sensors:
        sensors_data.append(
            {
                "name": name,
                "temp": data.get(t_key, "-"),
                "hum": data.get(h_key, "-") if h_key else "-",
                "pres": data.get(p_key, "-") if p_key else "-",
                "t": _to_float(data.get(t_key)) if t_key else None,
                "h": _to_float(data.get(h_key)) if h_key else None,
                "p": _to_float(data.get(p_key)) if p_key else None,
            }
        )

    reference = _pick_reference(sensors_data)
    ref_name = reference["name"] if reference else "-"
    ref_t = reference["t"] if reference else None
    ref_h = reference["h"] if reference else None
    ref_p = reference["p"] if reference else None

    rows = []
    for sensor in sensors_data:
        rows.append(
            "<tr><td>{name}</td><td>{temp}</td><td>{hum}</td><td>{pres}</td><td>{dt}</td><td>{dh}</td><td>{dp}</td></tr>".format(
                name=sensor["name"],
                temp=sensor["temp"],
                hum=sensor["hum"],
                pres=sensor["pres"],
                dt=_fmt_delta(sensor["t"], ref_t),
                dh=_fmt_delta(sensor["h"], ref_h),
                dp=_fmt_delta(sensor["p"], ref_p),
            )
        )
    return "".join(rows), ref_name


def _fmt_datetime(ts):
    if not ts or len(ts) < 6:
        return "-"
    return "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
        ts[0], ts[1], ts[2], ts[3], ts[4], ts[5]
    )


def render_html(data, refresh_seconds=8, ntp_message=None, current_dt=None):
    comparison_rows, reference_name = _render_compare_rows(data)
    ntp_banner = ""
    if ntp_message:
        ntp_banner = '<div class="ntp-banner">{}</div>'.format(ntp_message)
    current_time = _fmt_datetime(current_dt)
    return """<html>
    <head>
      <title>Pico2 Weather Debug</title>
      <meta http-equiv="refresh" content="{refresh}">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        html {{font-family: Arial; text-align: center;}}
        body {{margin: 0; background: #f4f5f7; color: #1c2330;}}
        .topnav {{background: #f8af73; padding: 12px;}}
        .cards {{max-width: 980px; margin: 1rem auto; display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));}}
        .card {{background: #fff; border-radius: 8px; padding: 0.8rem; box-shadow: 2px 2px 10px rgba(0,0,0,.15);}}
        .reading {{font-size: 1.6rem;}}
        .compare-wrap {{max-width: 980px; margin: 1rem auto 2rem; background: #fff; border-radius: 8px; box-shadow: 2px 2px 10px rgba(0,0,0,.15); padding: 0.8rem;}}
        .compare-table {{width: 100%; border-collapse: collapse;}}
        .compare-table th, .compare-table td {{border: 1px solid #ddd; padding: 0.5rem;}}
        .compare-table th {{background: #f1f3f5;}}
        .actions {{max-width: 980px; margin: 1rem auto; text-align: center;}}
        .btn {{display: inline-block; background: #1c2330; color: #fff; text-decoration: none; padding: 0.5rem 0.9rem; border-radius: 6px;}}
        .ntp-banner {{max-width: 980px; margin: 0.5rem auto 0; background: #e9f7ef; color: #1b5e20; border: 1px solid #c8e6c9; border-radius: 8px; padding: 0.6rem;}}
      </style>
    </head>
    <body>
      <div class="topnav"><h2>Rpi Pico2-w Weather testing server</h2><p>Date and time: {current_time}</p></div>
      <div class="actions"><a class="btn" href="/sync-ntp">Sync NTP now</a></div>
      {ntp_banner}
      <div class="cards">
        <div class="card"><h4>Temperature</h4><p class="reading">{temp} C</p></div>
        <div class="card"><h4>Humidity</h4><p class="reading">{hum} %</p></div>
        <div class="card"><h4>Pressure</h4><p class="reading">{pres} hPa</p></div>
        <div class="card"><h4>Gas</h4><p class="reading">{gas} kOhm</p></div>
        <div class="card"><h4>Wind Speed</h4><p class="reading">{wspd} km/h</p></div>
        <div class="card"><h4>Wind Direction</h4><p class="reading">{wdir} ({wdeg} deg)</p></div>
        <div class="card"><h4>Rain (interval)</h4><p class="reading">{rain} mm</p></div>
        <div class="card"><h4>Rain (total)</h4><p class="reading">{raint} mm</p></div>
      </div>
      <div class="compare-wrap">
        <h3>Sensor comparison (reference: {reference_name})</h3>
        <table class="compare-table">
          <thead>
            <tr><th>Sensor</th><th>Temperature (C)</th><th>Humidity (%)</th><th>Pressure (hPa)</th><th>Delta T</th><th>Delta H</th><th>Delta P</th></tr>
          </thead>
          <tbody>
            {comparison_rows}
          </tbody>
        </table>
      </div>
    </body>
    </html>""".format(
        refresh=refresh_seconds,
        temp=_first(data, ["temperature_c", "sensor_bme680_temperature_c", "sensor_bme280_temperature_c", "sensor_aht20_temperature_c", "sensor_dht22_temperature_c"]),
        hum=_first(data, ["humidity_pct", "sensor_bme680_humidity_pct", "sensor_aht20_humidity_pct", "sensor_dht22_humidity_pct"]),
        pres=_first(data, ["pressure_hpa", "sensor_bme680_pressure_hpa", "sensor_bme280_pressure_hpa"]),
        gas=_first(data, ["gas_kohms", "sensor_bme680_gas_kohms"]),
        wspd=data.get("wind_speed_kmh", "-"),
        wdir=data.get("wind_dir_cardinal", "-"),
        wdeg=data.get("wind_dir_deg", "-"),
        rain=data.get("rain_mm", "-"),
        raint=data.get("rain_mm_total", "-"),
        comparison_rows=comparison_rows,
        reference_name=reference_name,
        ntp_banner=ntp_banner,
        current_time=current_time,
    )
