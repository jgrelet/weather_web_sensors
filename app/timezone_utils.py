import time


DEFAULT_TIMEZONE = {
    "name": "Europe/Paris",
    "standard_offset_minutes": 60,
    "dst_offset_minutes": 120,
    "dst_rule": "eu",
    "standard_abbrev": "CET",
    "dst_abbrev": "CEST",
}


def _is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _days_in_month(year, month):
    if month == 2:
        return 29 if _is_leap_year(year) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def _day_of_year(year, month, day):
    total = 0
    current_month = 1
    while current_month < month:
        total += _days_in_month(year, current_month)
        current_month += 1
    return total + day


def _weekday(year, month, day):
    offsets = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    adjusted_year = year - 1 if month < 3 else year
    sunday_based = (
        adjusted_year
        + adjusted_year // 4
        - adjusted_year // 100
        + adjusted_year // 400
        + offsets[month - 1]
        + day
    ) % 7
    return (sunday_based - 1) % 7


def _last_sunday_day(year, month):
    days = _days_in_month(year, month)
    weekday = _weekday(year, month, days)
    return days - ((weekday + 1) % 7)


def get_timezone_config(app_cfg=None):
    cfg = dict(DEFAULT_TIMEZONE)
    if app_cfg:
        cfg.update(app_cfg.get("timezone", {}) or {})
    return cfg


def is_dst_active(utc_dt=None, tz_cfg=None):
    if utc_dt is None:
        utc_dt = time.localtime()
    if tz_cfg is None:
        tz_cfg = DEFAULT_TIMEZONE

    rule = str(tz_cfg.get("dst_rule", "none")).lower()
    if rule in ("none", "", "off", "false"):
        return False
    if rule != "eu":
        return False

    year, month, day, hour, _, _, _, _ = utc_dt
    if month < 3 or month > 10:
        return False
    if 3 < month < 10:
        return True

    march_switch_day = _last_sunday_day(year, 3)
    october_switch_day = _last_sunday_day(year, 10)
    if month == 3:
        return day > march_switch_day or (day == march_switch_day and hour >= 1)
    return day < october_switch_day or (day == october_switch_day and hour < 1)


def _offset_minutes_for_utc(utc_dt, tz_cfg):
    if is_dst_active(utc_dt, tz_cfg):
        return int(tz_cfg.get("dst_offset_minutes", tz_cfg.get("standard_offset_minutes", 0)))
    return int(tz_cfg.get("standard_offset_minutes", 0))


def localtime_from_utc(utc_dt=None, tz_cfg=None):
    if utc_dt is None:
        utc_dt = time.localtime()
    if tz_cfg is None:
        tz_cfg = DEFAULT_TIMEZONE

    year, month, day, hour, minute, second, weekday, _ = utc_dt
    total_minutes = hour * 60 + minute + _offset_minutes_for_utc(utc_dt, tz_cfg)

    while total_minutes < 0:
        total_minutes += 1440
        day -= 1
        weekday = (weekday - 1) % 7
        if day < 1:
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            day = _days_in_month(year, month)

    while total_minutes >= 1440:
        total_minutes -= 1440
        day += 1
        weekday = (weekday + 1) % 7
        if day > _days_in_month(year, month):
            day = 1
            month += 1
            if month > 12:
                month = 1
                year += 1

    hour = total_minutes // 60
    minute = total_minutes % 60
    yearday = _day_of_year(year, month, day)
    return (year, month, day, hour, minute, second, weekday, yearday)


def timezone_name(utc_dt=None, tz_cfg=None):
    if utc_dt is None:
        utc_dt = time.localtime()
    if tz_cfg is None:
        tz_cfg = DEFAULT_TIMEZONE
    if is_dst_active(utc_dt, tz_cfg):
        return tz_cfg.get("dst_abbrev", tz_cfg.get("name", "DST"))
    return tz_cfg.get("standard_abbrev", tz_cfg.get("name", "STD"))


def format_datetime(dt):
    if not dt or len(dt) < 6:
        return "-"
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        dt[0], dt[1], dt[2], dt[3], dt[4], dt[5]
    )
