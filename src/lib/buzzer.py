from machine import Pin
import time

class Buzzer:

    def __init__(self, pin):
        self.trigger = pin
        self.double_quick_beep()

    def start(self):
        self.trigger.value(0) # Buzzer ON

    def stop(self):
        self.trigger.value(1) # Buzzer OFF

    def quick_beep(self, n=1):
        for n in range(n):
            self.start() # Buzzer ON
            time.sleep(0.2)
            self.stop() # Buzzer OFF
            time.sleep(0.2)

    def double_quick_beep(self):
        self.start() # Buzzer ON
        time.sleep(0.2)
        self.stop() # Buzzer OFF
        time.sleep(0.2)
        self.start() # Buzzer ON
        time.sleep(0.2)
        self.stop() # Buzzer OFF
