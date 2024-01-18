import time
import pycom
import sys
import machine
import micropython
import ubinascii
import helpers.led_control as led_control
from helpers.colors import Colors
from machine import Timer

from network import WLAN

from button import Button
from machine import UART
from machine import Pin
from pysense import Pysense

#from mqtt import MQTTClient

from LIS2HH12 import LIS2HH12 # Accelerometer
from SI7006A20 import SI7006A20 # Temperature and humidity
from LTR329ALS01 import LTR329ALS01 # Ligth sensor
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE # barometer
from MH_Z19B import MH_Z19B # CO2 sensor
from buzzer import Buzzer


from machine import RTC

CONCENTRATION_THRESHOLD = 800 # PPM

def confgureAccessPoint():
    wlan = WLAN(mode=WLAN.AP, ssid="ROOM_E356", auth=(WLAN.WPA2, "CO2_B5GHUB")) # default IP is 192.168.4.1

def stablish_wifi_connection(ssid_=None, passwd= None):
    wlan = WLAN(mode=WLAN.STA)
    if not ssid_:
        ssid_ = "eduroam"
        wlan.connect(ssid=ssid_, auth=(WLAN.WPA2_ENT, "david.tena@uws.ac.uk", "DtenGag1998_UWS"), identity="david.tena@uws.ac.uk", timeout=100000)
    elif ssid_ is not None and passwd is not None:
        wlan.connect(ssid=ssid_, auth=(WLAN.WPA2, passwd), timeout=5000)
    else:
        print("ERROR: WiFi connection could not be stablished. SSID or Password were not given correctly")

    print("Attempting to create WiFi connection to SSID ", ssid_ ,"...")
    while not wlan.isconnected():
        machine.idle() # save power while waiting
    print('WLAN connection succeeded!. Connection information (IP, netmask, gateway, DNS):', wlan.ifconfig())
    led_control.blink(Colors.LED_WHITE)
    return wlan

def update_state(buzzer, co2_concentration, co2_limit_last_iter):
    limit_reached = co2_concentration >= CONCENTRATION_THRESHOLD

    if co2_concentration == -1: # CRC errors
        led_control.constant_orange()
        return -1
    else: # No CRC erros
        if co2_limit_last_iter == False and co2_concentration != -1: # First time no CRC errors
            led_control.blue_heartbeat()

        if limit_reached:
            if co2_limit_last_iter == False: # First time concentration limit is reached
                led_control.constant_red()
                buzzer.quick_beep()
            return True
        elif not limit_reached:
            if co2_limit_last_iter == True: # First time concentration is not reached
                led_control.blue_heartbeat()
            return False

def measure_co2(co2_sensor):
    return co2_sensor.read_co2()

def measure_temp_and_hum(temp_and_hum):
    return temp_and_hum.temperature(), temp_and_hum.humidity()

def measure_altitude(altitude):
    return altitude.altitude()

def measure_pressure(pressure):
    return pressure.pressure()

def measure_light(light):
    return light.light()

def measure_accelerometer(acc):
    return acc.acceleration(), acc.roll(), acc.pitch()

def calibrate_co2_sensor(buzzer, co2_sensor, span=None):
    buzzer.quick_beep(3)
    led_control.constant_green()

    if span is None:
        finish = co2_sensor.calibrate_zero_point()
    else:
        finish = co2_sensor.calibrate_span(span)
    while not finish:
        machine.idle()

    led_control.blue_heartbeat()
    buzzer.double_quick_beep()

def main(mode="online"):
    buzzer = Buzzer(Pin('P9', mode=Pin.OUT))
    co2_sensor = MH_Z19B(UART(1, 9600, bits=8, parity=None, stop=1,  pins=('P10','P11'))) # pins(TXD, RXD)
    button = Button()
    button.on()

    led_control.blue_heartbeat()

    # connect to WiFI network
    if mode == "online":
        wlan = stablish_wifi_connection(ssid_="RAMBOT_POST_LOVEYOU", passwd="28532538") # RAMBOT_POST_LOVEYOU password is 28532538
        #wlan = stablish_wifi_connection() # No connection configuration if connecting to eduroam

    # Create sensors
    py = Pysense()
    acc = LIS2HH12(py)
    temp_and_hum = SI7006A20(py)
    light = LTR329ALS01(py)
    altitude = MPL3115A2(py, mode=ALTITUDE)
    pressure = MPL3115A2(py, mode=PRESSURE)

    co2_limit_last_iter = False
    while True:
        if button.pressed == True:
            calibrate_co2_sensor(buzzer, co2_sensor)
            button.pressed = False
        else:
            co2_limit_last_iter = iterate(buzzer, co2_sensor, acc, temp_and_hum, light, altitude, pressure, co2_limit_last_iter)
        time.sleep(10)

def iterate(buzzer, co2_sensor, acc, temp_and_hum, light, altitude, pressure, co2_limit_last_iter, print_results=True):
    val_co2_concentration = measure_co2(co2_sensor)
    val_temperature, val_rel_humidity = measure_temp_and_hum(temp_and_hum)
    val_altitude = measure_altitude(altitude)
    val_pressure = measure_pressure(pressure)
    val_light = measure_light(light)
    val_acceleration, val_roll, val_pitch  = measure_accelerometer(acc)

    if print_results:
        print(  "CO2 concentration: " + str(val_co2_concentration) + " PPM\n"
                "Temperature: " + str(val_temperature) + " degrees C\n" +
                "Relative humidity: " + str(val_rel_humidity) + " %\n" +
                "Altitude: " + str(val_altitude) + "  metres\n" +
                "Pressure: " + str(val_pressure) + " Pascals\n" +
                "Light (channel Blue lux, channel Red lux): " + str(val_light) + "\n" +
                "Acceleration: " + str(val_acceleration) + "\n" +
                "Roll: " + str(val_roll) + "\n" +
                "Pitch: " + str(val_pitch) +
                "\n----------------------------------------\n",
                end="\r")
    return update_state(buzzer, val_co2_concentration, co2_limit_last_iter)

if __name__ == '__main__':
    confgureAccessPoint()
    main(mode="offline")
