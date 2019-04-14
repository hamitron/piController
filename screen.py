from smbus2 import SMBusWrapper
import time
import RPi.GPIO as GPIO
import atexit
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

pin=40
resetPin=38
boardAddress=0x3D
oledAddress=0x3C

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(resetPin, GPIO.OUT)

display = Adafruit_SSD1306.SSD1306_128_64(rst=None, gpio=GPIO, i2c_bus=1, i2c_address=oledAddress)
font = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf', 8)
image = Image.new('1', (128,64))
draw = ImageDraw.Draw(image)

def resetBoard():
    GPIO.output(resetPin, GPIO.LOW)
    GPIO.output(resetPin, GPIO.HIGH)

@atexit.register
def revert():
    print "Goodbye"
    display.clear()
    resetBoard()
    GPIO.cleanup()

def read(address):
    with SMBusWrapper(1) as bus:
        b = bus.read_i2c_block_data(boardAddress, address, 1)
        return b

def displayText(txt):
    print txt

def oledDisplay():
    display.clear()
    draw.rectangle((0,0,128,64), outline=1, fill=0)
    draw.text((30,0), "text", font=font, fill=255)
    display.image(image)
    display.display()

def pinCallback(channel):
    value = read(0x01)
    if value == 34:
        displayText("Turn Right")    
    if value == 33:
        displayText("turn left")
    if value == 69:
        displayText("big button")
    if value == 73:
        displayText("left button")
    if value == 77:
        displayText("middle button")
    else:
        displayText("unknown")

display.begin()
display.display()
GPIO.add_event_detect(pin, GPIO.BOTH, callback=pinCallback)
while True:
    print "heartbeat"
    time.sleep(3)
    oledDisplay()
