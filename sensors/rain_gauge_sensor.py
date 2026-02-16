from machine import Pin


class RainGaugeSensor:
    def __init__(self, pin=15, pull_up=True, mm_per_tip=0.2794):
        mode = Pin.PULL_UP if pull_up else None
        self._pin = Pin(pin, Pin.IN, mode) if mode is not None else Pin(pin, Pin.IN)
        self._mm_per_tip = mm_per_tip
        self._tips = 0
        self._total_tips = 0
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._on_tip)

    def _on_tip(self, _pin):
        self._tips += 1
        self._total_tips += 1

    def read(self):
        tips = self._tips
        self._tips = 0
        return {
            "rain_tips": tips,
            "rain_mm": round(tips * self._mm_per_tip, 3),
            "rain_mm_total": round(self._total_tips * self._mm_per_tip, 3),
        }
