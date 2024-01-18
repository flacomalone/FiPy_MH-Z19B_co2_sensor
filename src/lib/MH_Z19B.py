import time
import struct

class MH_Z19B:
    def __init__(self, uart, verbose=False):
        self.uart = uart
        self.verbose = verbose
        self.set_detection_range_0_5000()
        time.sleep(0.25)
        self.set_autocalibration_ON()
        time.sleep(0.25)

    def read_co2(self):
        self.uart.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')

        received = False
        buf = None
        while True:
            buf = self.uart.readline() # read(9)
            if buf is None:
                continue
                #print("waiting for response")
            else:
                break

        if self.is_valid(buf):
            co2 = buf[2] * 256 + buf[3]
            del buf
            return co2
        else:
            del buf
            return -1

    def is_valid(self, buf):
        if buf is None or buf[0] != 0xFF or buf[1] != 0x86:
            return False
        i = 1
        checksum = 0x00
        while i < 8:
            checksum += buf[i] % 256
            i += 1
        checksum = ~checksum & 0xFF
        checksum += 1
        return checksum == buf[8]

    def calibrate_zero_point(self):
        self.uart.write(b'\xff\x01\x87\x00\x00\x00\x00\x00\x78')
        if self.verbose:
            print("MH-X19B CO2 sensor -> Calibration request has been sent. Sensor shoud keep in a 400 ppm environment for the next 20 minutes")
        t = 20 * 60
        while t:
            mins, secs = divmod(t, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            print("Calibration time remaining: ", timeformat, end='\r')
            time.sleep(1)
            t -= 1
        if self.verbose:
            print("MH-X19B CO2 sensor -> Calibration finished")
        return 1

    def checksum(self, array):
        return struct.pack('B', 0xff - (sum(array) % 0x100) + 1)

    # TODO needs to be fixed I belive
    def calibrate_span(self, span): # Calibrate sensor to a given concentration
        b3 = span // 256
        byte3 = struct.pack('B', b3)
        b4 = span % 256
        byte4= struct.pack('B', b4)
        c = self.checksum([0x01, 0x88, b3, b4])
        request = b"\xff\x01\x88" + byte3 + byte4 + b"\x00\x00\x00" + c
        self.uart.write(request)
        if self.verbose:
            print("MH-X19B CO2 sensor -> Calibration request has been sent. Sensor shoud keep in a " + str(span) + " ppm environment for the next 20 minutes")

        t = 20 * 60
        while t:
            mins, secs = divmod(t, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            if self.verbose:
                print("Calibration time remaining: ", timeformat, end='\r')
            time.sleep(1)
            t -= 1
        if self.verbose:
            print("MH-X19B CO2 sensor -> Calibration finished")
        return 1


    def set_autocalibration_ON(self):
        self.uart.write(b'\xff\x01\x79\xA0\x00\x00\x00\x00\xE6')
        if self.verbose:
            print("MH-X19B CO2 sensor -> Autocalibration mode is set to ON")

    def set_autocalibration_off(self):
        self.uart.write(b'\xff\x01\x79\x00\x00\x00\x00\x00\x86')
        if self.verbose:
            print("MH-X19B CO2 sensor -> Autocalibration mode is set to OFF")

    def set_detection_range_0_2000(self, uart):
        uart.write(b'\xff\x01\x99\x00\x00\x00\x07\xD0\x8F')
        if self.verbose:
            print("MH-X19B CO2 sensor -> Detection range has been set from 0 to 2000 ppm")

    def set_detection_range_0_5000(self):
        self.uart.write(b'\xff\x01\x99\x00\x00\x00\x13\x88\xcb')
        if self.verbose:
            print("MH-X19B CO2 sensor -> Detection range has been set from 0 to 5000 ppm")

    def set_detection_range_0_10000(self):
        self.uart.write(b'\xff\x01\x99\x00\x00\x00\x27\x10\x2F')
        if self.verbose:
            print("MH-X19B CO2 sensor -> Detection range has been set from 0 to 10000 ppm")
