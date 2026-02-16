from machine import I2C, Pin
from time import sleep_ms
from bme680 import BME680_I2C
from bmp280 import BMP280I2C


class BME680Sensor:
    def __init__(
        self,
        i2c_id=0,
        sda_pin=0,
        scl_pin=1,
        i2c_freq=200000,
        address=None,
        temp_offset_c=0.0,
        humidity_offset_pct=0.0,
        pressure_offset_hpa=0.0,
    ):
        self.i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=i2c_freq)
        self.sensor, self._sensor_kind = self._init_sensor(address)
        self.temp_offset_c = temp_offset_c
        self.humidity_offset_pct = humidity_offset_pct
        self.pressure_offset_hpa = pressure_offset_hpa
        sleep_ms(200)

    def _read_chip_id(self, address):
        try:
            return self.i2c.readfrom_mem(address, 0xD0, 1)[0]
        except OSError:
            return None

    def _init_sensor(self, configured_address):
        if configured_address is None:
            candidate_addresses = [0x76, 0x77]
        else:
            candidate_addresses = [configured_address]

        scanned = self.i2c.scan()
        chip_ids = {}
        for address in candidate_addresses:
            if address in scanned:
                chip_ids[address] = self._read_chip_id(address)

        for address in candidate_addresses:
            if chip_ids.get(address) == 0x61:
                return BME680_I2C(i2c=self.i2c, address=address), "bme680"

        for address, chip_id in chip_ids.items():
            if chip_id == 0x58:
                print(
                    "I2C 0x%02X reports chip_id 0x58; using BMP280/BME280 compatibility mode."
                    % address
                )
                return BMP280I2C(address, self.i2c), "bmp280"

        raise RuntimeError(
            "BME680/BMP280 not found. I2C devices=%s chip_ids=%s"
            % ([hex(a) for a in scanned], {hex(k): hex(v) for k, v in chip_ids.items()})
        )

    def read(self):
        if self._sensor_kind == "bmp280":
            measurements = self.sensor.measurements
            return {
                "temperature_c": round(measurements["t"] + self.temp_offset_c, 2),
                "pressure_hpa": round(measurements["p"] + self.pressure_offset_hpa, 2),
                "sensor_bme680_temperature_c": round(
                    measurements["t"] + self.temp_offset_c, 2
                ),
                "sensor_bme680_pressure_hpa": round(
                    measurements["p"] + self.pressure_offset_hpa, 2
                ),
            }

        return {
            "temperature_c": round(self.sensor.temperature + self.temp_offset_c, 2),
            "humidity_pct": round(self.sensor.humidity + self.humidity_offset_pct, 2),
            "pressure_hpa": round(self.sensor.pressure + self.pressure_offset_hpa, 2),
            "gas_kohms": round((self.sensor.gas or 0) / 1000, 2),
            "sensor_bme680_temperature_c": round(
                self.sensor.temperature + self.temp_offset_c, 2
            ),
            "sensor_bme680_humidity_pct": round(
                self.sensor.humidity + self.humidity_offset_pct, 2
            ),
            "sensor_bme680_pressure_hpa": round(
                self.sensor.pressure + self.pressure_offset_hpa, 2
            ),
            "sensor_bme680_gas_kohms": round((self.sensor.gas or 0) / 1000, 2),
        }
