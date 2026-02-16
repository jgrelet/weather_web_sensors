from machine import Pin
import time


class WindSpeedSensor:
    def __init__(self, pin=14, pull_up=True, kmh_per_hz=2.4):
        mode = Pin.PULL_UP if pull_up else None
        self._pin = Pin(pin, Pin.IN, mode) if mode is not None else Pin(pin, Pin.IN)
        self._kmh_per_hz = kmh_per_hz
        self._pulses = 0
        self._last_ms = time.ticks_ms()
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._on_pulse)

    def _on_pulse(self, _pin):
        self._pulses += 1

    def read(self):
        now = time.ticks_ms()
        elapsed_ms = time.ticks_diff(now, self._last_ms)
        if elapsed_ms <= 0:
            return {"wind_speed_kmh": 0.0, "wind_pulses": 0}

        pulses = self._pulses
        self._pulses = 0
        self._last_ms = now

        hz = pulses / (elapsed_ms / 1000)
        return {
            "wind_speed_kmh": round(hz * self._kmh_per_hz, 2),
            "wind_pulses": pulses,
        }
