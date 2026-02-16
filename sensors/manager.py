import time


class SensorManager:
    def __init__(self, sensors):
        self._sensors = sensors

    def read_all(self):
        payload = {
            "timestamp": time.time(),
        }
        for sensor in self._sensors:
            try:
                payload.update(sensor.read())
            except Exception as exc:
                name = sensor.__class__.__name__
                payload["error_" + name] = str(exc)
        return payload
