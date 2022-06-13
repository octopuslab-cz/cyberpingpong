# octopusLab spi-display 7 segment (8x)
# edition 2022/05
from machine import Pin, SPI
from utils.pinout import set_pinout
from components.display7 import Display7

pinout = set_pinout()
# octopusLab: setup() -> ds --> pinout

print("- spi init")
spi = SPI(1, baudrate=10000000, polarity=1, phase=0, sck=Pin(pinout.SPI_CLK_PIN), mosi=Pin(pinout.SPI_MOSI_PIN))
ss = Pin(pinout.SPI_CS0_PIN, Pin.OUT)

print("- display7 init")
def display7init():
    d7 = Display7(spi, ss) # 8 x 7segment display init
    d7.write_to_buffer('octopus')
    d7.display()
    return d7