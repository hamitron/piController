# raspberry pi control panel script
# button presses and knob turns perform actions

from smbus2 import SMBusWrapper
import time
import RPi.GPIO as GPIO
import atexit

pin=40
resetPin=38
operations = ["one", "two", "three", "four", "sbleventy"]
opIndex = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(resetPin, GPIO.OUT)

def resetBoard():
    GPIO.output(resetPin, GPIO.LOW)
    GPIO.output(resetPin, GPIO.HIGH)
    GPIO.output(resetPin, GPIO.LOW)

@atexit.register
def revert():
    print "Goodbye"
    resetBoard()
    GPIO.cleanup()

def read(address):
    with SMBusWrapper(1) as bus:
        b = bus.read_byte_data(0x3d, address)
        return b

def doLed(led):
    pwm = read(led)
    with SMBusWrapper(1) as bus:
        if pwm == 0:
            bus.write_byte_data(0x3d, led, 100)
        else:
            bus.write_byte_data(0x3d, led, 0)

def scrollThrough(direction):
    print direction

def pinCallback(channel):
    value = read(0x01)
    if value == 34:
       # print "turn right"
       scrollThrough("plus")
    if value == 33:
        scrollThrough("minus")
       # print "turn left"
    if value == 69:
        print "big button"
    if value == 73:
        doLed(0x21)
        print "left button"
    if value == 77:
        doLed(0x20)
        print "middle button"
    if value == 65:
        print "knob press"

GPIO.add_event_detect(pin, GPIO.BOTH, callback=pinCallback)
while True:
    time.sleep(3)

