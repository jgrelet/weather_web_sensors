from machine import ADC


class WindDirectionSensor:
    # ADC thresholds for common 16-position wind vanes.
    LOOKUP = [
        (150, 112.5, "ESE"),
        (350, 67.5, "ENE"),
        (550, 90.0, "E"),
        (800, 157.5, "SSE"),
        (1050, 135.0, "SE"),
        (1300, 202.5, "SSW"),
        (1600, 180.0, "S"),
        (1900, 22.5, "NNE"),
        (2200, 45.0, "NE"),
        (2500, 247.5, "WSW"),
        (2800, 225.0, "SW"),
        (3100, 337.5, "NNW"),
        (3400, 0.0, "N"),
        (3750, 292.5, "WNW"),
        (4050, 315.0, "NW"),
        (65535, 270.0, "W"),
    ]

    def __init__(self, adc_pin=26):
        self._adc = ADC(adc_pin)

    def read(self):
        value = self._adc.read_u16()
        for threshold, degrees, cardinal in self.LOOKUP:
            if value <= threshold:
                return {
                    "wind_dir_raw": value,
                    "wind_dir_deg": degrees,
                    "wind_dir_cardinal": cardinal,
                }
        return {
            "wind_dir_raw": value,
            "wind_dir_deg": 0.0,
            "wind_dir_cardinal": "N",
        }
