# The MIT License (MIT)
#
# Copyright (c) 2019 Bryan Siepert for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_tlv493d`
================================================================================

CircuitPython helper library for the TLV493D 3-axis magnetometer


* Author(s): Bryan Siepert

Implementation Notes
--------------------

**Hardware:**


Adafruit's TLV493D Breakout https://adafruit.com/products


**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

import struct
import adafruit_bus_device.i2c_device as i2cdevice
__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_TLV493D.git"
DEFAULT_TLV_ADDRESS = 0x5E


class TLV493D:
    """IT'S A CLASS"""

    read_masks = {
        "BX1": (0, 0xFF, 0),
        "BX2": (4, 0xF0, 4),
        "BY1": (1, 0xFF, 0),
        "BY2": (4, 0x0F, 0),
        "BZ1": (2, 0xFF, 0),
        "BZ2": (5, 0x0F, 0),
        "TEMP1": (3, 0xF0, 4),
        "TEMP2": (6, 0xFF, 0),
        "FRAMECOUNTER": (3, 0x0C, 2),
        "CHANNEL": (3, 0x03, 0),
        "POWERDOWNFLAG": (5, 0x10, 4),
        "RES1": (7, 0x18, 3),
        "RES2": (8, 0xFF, 0),
        "RES3": (9, 0x1F, 0)
    }

    write_masks = {
        "PARITY":(1, 0x80, 7),
        "ADDR":(1, 0x60, 5),
        "INT":(1, 0x04, 2),
        "FAST":(1, 0x02, 1),
        "LOWPOWER":(1, 0x01, 0),
        "TEMP_DISABLE":(3, 0x80, 7),
        "LP_PERIOD":(3, 0x40, 6),
        "POWERDOWN":(3, 0x20, 5),
        "RES1":(1, 0x18, 3),
        "RES2":(2, 0xFF, 0),
        "RES3":(3, 0x1F, 0)
    }

    def __init__(self, i2c_interface, i2c_address=DEFAULT_TLV_ADDRESS):
        self.i2c_device = i2cdevice.I2CDevice(i2c_interface, i2c_address)
        self.read_buffer = bytearray(10)
        self.write_buffer = bytearray(4)
        self._setup_write_buffer()

        # // get all register data from sensor
        # tlv493d::readOut(&mInterface);
        # // copy factory settings to write registers
        # setRegBits(tlv493d::W_RES1, getRegBits(tlv493d::R_RES1)); THREE TIMES?
        # // enable parity detection
        
        print("\nWrite buffer:")
        self.print_bytes(self.write_buffer)
        self._set_write_key('PARITY', 1);
        print("\nWrite buffer:")
        self.print_bytes(self.write_buffer)
        # // config sensor to lowpower mode
        # // also contains parity calculation and writeout to sensor
        # setAccessMode(TLV493D_DEFAULTMODE);        
        self._set_write_key('PARITY', 1);
        self._set_write_key('LOWPOWER', 1);
        self._set_write_key('LP_PERIOD', 1);
        print("\nWrite buffer:")
        self.print_bytes(self.write_buffer)
        self._write_i2c()
        print("wrote output buffer out")

    def _read_i2c(self):
        with self.i2c_device as i2c:
            i2c.readinto(self.read_buffer)
        # self.print_bytes(self.read_buffer)

    @staticmethod
    def print_bytes(bites):
        """DOC STRING"""
        for byte in bites:
            print("%s (%s)"%(bin(byte), hex(byte)))

    def _write_i2c(self):
        with self.i2c_device as i2c:
            i2c.write(self.write_buffer)

    def _setup_write_buffer(self):
        self._read_i2c()
        print("Read buffer:")
        self.print_bytes(self.read_buffer)
        print("\nWrite buffer:")
        self.print_bytes(self.write_buffer)

        for key in ['RES1', 'RES2', 'RES3']:
            write_value = self._get_read_key(key)
            self._set_write_key(key, write_value)
        print("Read buffer:")
        self.print_bytes(self.read_buffer)
        print("\nWrite buffer:")
        self.print_bytes(self.write_buffer)

    def _get_read_key(self, key):
        read_byte_num, read_mask, read_shift = self.read_masks[key]
        raw_read_value = self.read_buffer[read_byte_num]
        write_value = (raw_read_value & read_mask)>>read_shift
        return write_value

    def _set_write_key(self, key, value):
        write_byte_num, write_mask, write_shift = self.write_masks[key]
        current_write_byte = self.write_buffer[write_byte_num]
        current_write_byte &= ~write_mask
        current_write_byte |= value<<write_shift
        self.write_buffer[write_byte_num] = current_write_byte

    @property
    def x(self):
        self._read_i2c()
        x_top = self._get_read_key("BX1")
        x_bot = self._get_read_key("BX2")
        x_val = x_top<<4 | x_bot
        xtop = (x_val & 0xFF00)>>8
        xbot = (x_val & 0x00FF)
        binval = struct.unpack_from(">h", bytearray([xtop, xbot]))[0] 
        return binval

    @property
    def y(self):
        self._read_i2c()
        y_top = self._get_read_key("BY1")
        y_bot = self._get_read_key("BY2")
        y_val = y_top<<4 | y_bot
        ytop = (y_val & 0xFF00)>>8
        ybot = (y_val & 0x00FF)
        binval = struct.unpack_from(">h", bytearray([ytop, ybot]))[0] 
        return binval

    @property
    def z(self):
        self._read_i2c()
        z_top = self._get_read_key("BZ1")
        z_bot = self._get_read_key("BZ2")
        z_val = z_top<<4 | z_bot
        ztop = (z_val & 0xFF00)>>8
        zbot = (z_val & 0x00FF)
        binval = struct.unpack_from(">h", bytearray([ztop, zbot]))[0] 
        return binval
