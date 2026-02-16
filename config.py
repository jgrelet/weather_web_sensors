"""
Wi-Fi configuration.

Recommended workflow:
- Keep real credentials in `wifi_secrets.py` on the Pico (and optionally local, gitignored).
- Keep placeholders here for source control safety.
"""

try:
    from wifi_secrets import ssid, password
except ImportError:
    ssid = "xxxxxxxx"  # Your network name
    password = "xxxxxxxx"  # Your WiFi password
