import time
import board
import adafruit_tlv493d

i2c = board.I2C()

tlv = adafruit_tlv493d.TLV493D(i2c)

while True:
    print("%s, %s, %s"%tlv.magnetic)
    time.sleep(1)