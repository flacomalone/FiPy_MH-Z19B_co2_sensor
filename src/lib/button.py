from machine import Pin
import time

class Button:
    def __init__(self):
        self.pressed = False
        self.btn = Pin("P14", mode=Pin.IN, pull=Pin.PULL_UP)
        self.on()

    def on(self):
        self.btn.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING,
                          self._handler)
    def off(self):
        self.btn.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING,
                          None)

    def _handler(self, pin):
        value = pin.value()
        if not value:
            print("Button pressed")
            self.pressed = True
        else:
            pass
