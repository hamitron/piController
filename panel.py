# raspberry pi control panel script
# button presses and knob turns perform actions

from smbus2 import SMBusWrapper
import time
import RPi.GPIO as GPIO
import atexit
import constant

class PanelController:

    def __init__(self):
        self.operations = {
            33: "knob turn right",
            34: "knob turn left",
            65: "knob button",
            69: "white button",
            73: "soft button left",
            77: "soft button right"
        }

        self.opIndex = 0

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(constant.DETECT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(constant.RESET, GPIO.OUT)

        # watches int pin event 
        GPIO.add_event_detect(constant.DETECT, GPIO.BOTH, callback=self.pinCallback)

    @atexit.register
    def resetBoard():
        GPIO.output(constant.RESET, GPIO.LOW)
        GPIO.output(constant.RESET, GPIO.HIGH)
        GPIO.output(constant.RESET, GPIO.LOW)
        GPIO.cleanup()
        print "Goodbye"

    def keepAlive(self):
        while True:
            print "heartbeat"
            time.sleep(3)

    def read(self, address):
        with SMBusWrapper(1) as bus:
            b = bus.read_byte_data(constant.DEVICE_ADDR, address)
            return b

    def doLed(self, led):
        pwm = read(led)
        with SMBusWrapper(1) as bus:
            if pwm == constant.PWM_LOW:
                bus.write_byte_data(constant.DEVICE_ADDR, led, constant.PWM_HIGH)
            else:
                bus.write_byte_data(constant.DEVICE_ADDR, led, constant.PWM_LOW)

    def scrollThrough(self, direction):
        print direction

    def pinCallback(self, channel):
        value = self.read(constant.READ_ADDR)
        if value in self.operations:
            print self.operations[value]

