SENSORS = {
    # Primary weather station bus (I2C1): SSD1306 + DS3231 + BME680
    "i2c": {
        "id": 1,
        "sda_pin": 2,
        "scl_pin": 3,
        "freq": 200000,
    },
    # Auxiliary bus (I2C0): AHT20 + BME280
    "i2c_aux": {
        "id": 0,
        "sda_pin": 4,
        "scl_pin": 5,
        "freq": 200000,
    },
    "display": {
        "enabled": True,
        "share_sensor_i2c": True,
        "id": 1,
        "sda_pin": 2,
        "scl_pin": 3,
        "freq": 200000,
        "addr": 0x3C,
    },
    "bme680": {
        "enabled": True,
        "address": 0x77,  # Set to 0x76 or 0x77. Use None for auto-detect.
        "temp_offset_c": 0.0,
        "humidity_offset_pct": 0.0,
        "pressure_offset_hpa": 0.0,
    },
    "bme280": {
        "enabled": True,
        "address": 0x77,
    },
    "aht20": {
        "enabled": True,
        "address": 0x38,
    },
    "rtc": {
        "enabled": True,
        "address": 0x68,
    },
    "eeprom": {
        "enabled": True,
        "address": 0x57,  # AT24C32 commonly bundled with DS3231 modules.
    },
    "dht22": {
        "enabled": True,
        "pin": 13,
        "min_interval_ms": 2000,
    },
    "wind_speed": {
        "enabled": True,
        "pin": 14,
        "pull_up": True,
        "kmh_per_hz": 2.4,
    },
    "wind_dir": {
        "enabled": True,
        "adc_pin": 26,
    },
    "rain_gauge": {
        "enabled": True,
        "pin": 15,
        "pull_up": True,
        "mm_per_tip": 0.2794,
    },
}

EXPORTS = {
    "mqtt": {
        "enabled": True,
        "broker": "192.168.1.70",
        "port": 1883,
        "topic": "weather/sensors",
        "client_id": "pico2-weather",
        "user": None,
        "password": None,
        "keepalive": 60,
        "ssl": False,
        "qos": 0,
        "retain": False,
    },
    "serial": {
        "enabled": False,
        "prefix": "JSON",
    },
    "udp": {
        "enabled": False,
        "host": "192.168.1.52",
        "port": 9999,
    },
    "lorawan": {
        "enabled": False,
        "port": 1,
    },
}

APP = {
    "timezone": {
        "name": "Europe/Paris",
        "standard_offset_minutes": 60,
        "dst_offset_minutes": 120,
        "dst_rule": "eu",  # "eu" or "none"
        "standard_abbrev": "CET",
        "dst_abbrev": "CEST",
    },
    # NTP policy:
    # - "never": never sync from NTP
    # - "always": sync at every boot
    # - "auto": sync only if RTC/system year is below ntp_min_year
    # - "pin": sync only when ntp_trigger_pin is active at boot
    "ntp_sync_mode": "auto",
    "ntp_min_year": 2024,
    "ntp_trigger_pin": None,  # Example: 22
    "ntp_trigger_active_high": True,
    "ntp_trigger_pull": "up",  # "up", "down", or None
    "use_ntp": True,  # Legacy compatibility; ignored when ntp_sync_mode is set.
    "timing_profile": "test",  # "test" or "prod"
    "timing_profiles": {
        "test": {
            "acquisition_interval_seconds": 10,
            "aggregation_interval_seconds": 60,
            "web_refresh_seconds": 10,
        },
        "prod": {
            "acquisition_interval_seconds": 60,
            "aggregation_interval_seconds": 3600,
            "web_refresh_seconds": 60,
        },
    },
}

_timing_profile_name = APP.get("timing_profile", "prod")
_timing_profiles = APP.get("timing_profiles", {})
_timing_profile = _timing_profiles.get(_timing_profile_name, _timing_profiles.get("prod", {}))

APP["acquisition_interval_seconds"] = _timing_profile.get("acquisition_interval_seconds", 60)
APP["aggregation_interval_seconds"] = _timing_profile.get("aggregation_interval_seconds", 3600)
APP["web_refresh_seconds"] = _timing_profile.get("web_refresh_seconds", 60)
