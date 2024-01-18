from .colors import Colors
import pycom
import time

def blue_heartbeat():
    pycom.heartbeat(False)
    pycom.rgbled(Colors.LED_BLUE) # Turn led green
    pycom.heartbeat(True)

def constant_green():
    pycom.heartbeat(False)
    pycom.rgbled(Colors.LED_GREEN) # Turn led green

def constant_orange():
    pycom.heartbeat(False)
    pycom.rgbled(Colors.LED_ORANGE) # Turn on orange LED

def constant_red():
    pycom.heartbeat(False)
    pycom.rgbled(Colors.LED_RED)

def blink(color):
    if color is None:
        print("ERROR: color code not defined")
    pycom.heartbeat(False)
    pycom.rgbled(color)
    time.sleep(0.3)
    pycom.rgbled(Colors.LED_OFF)
    time.sleep(0.3)
    pycom.rgbled(color)
    time.sleep(0.3)
    pycom.rgbled(Colors.LED_OFF)
    pycom.heartbeat(True)
    blue_heartbeat()
