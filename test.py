from smbus2 import SMBusWrapper
import time
import RPi.GPIO as GPIO
import atexit

#bus=smbus.SMBus(1)
pin=40
resetPin=38

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(resetPin, GPIO.OUT)

def resetBoard():
    GPIO.output(resetPin, GPIO.LOW)
    GPIO.output(resetPin, GPIO.HIGH)

@atexit.register
def revert():
    print "Goodbye"
    resetBoard()
    GPIO.cleanup()

def read(address):
    with SMBusWrapper(1) as bus:
        b = bus.read_byte_data(0x3d, address)
        return b

def pinCallback(channel):
    value = read(0x01)
    if value == 34:
        print "turn right"
    if value == 33:
        print "turn left"
    if value == 69:
        print "big button"
    if value == 73:
        print "left button"
    if value == 77:
        print "middle button"
    if value == 65:
        print "knob press"

GPIO.add_event_detect(pin, GPIO.BOTH, callback=pinCallback)
while True:
    time.sleep(3)

#while True:
 #   time.sleep(10)
  #  print "staying alive"
 #   pinValue=GPIO.input(pin)

  #  if pinValue == 0:
   #     read(0x01)
       # val=bus.read_i2c_block_data(0x3d,0x01,1)
    #    time.sleep(2)
    #else:
     #   time.sleep(2)

