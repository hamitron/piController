# raspberry pi control panel script
# button presses and knob turns perform actions

from smbus2 import SMBusWrapper
import time
import RPi.GPIO as GPIO
import atexit
import constant
import subprocess

class PanelController:

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

        self.cameraOn = False
        self.cameraProc = None

        self.operations = {
            33: "turn right",
            34: "knob turn left",
            65: "knob button",
            69: "white button",
            73: "soft button left",
            77: "soft button right"
        }
        
        self.menuOptions = ["Take Photo", "Shoot Video", "Settings", "Shut Down"]

        self.menuIndex = 0

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
            time.sleep(3)

    def read(self, address):
        with SMBusWrapper(1) as bus:
            b = bus.read_byte_data(constant.DEVICE_ADDR, address)
            return b

    def doLed(self, led):
        pwm = self.read(led)
        with SMBusWrapper(1) as bus:
            if pwm == constant.PWM_LOW:
                bus.write_byte_data(constant.DEVICE_ADDR, led, constant.PWM_HIGH)
            else:
                bus.write_byte_data(constant.DEVICE_ADDR, led, constant.PWM_LOW)

    def scroll(self, direction):
        statement = self.menuOptions[self.menuIndex] 
        print "\033[44;33m" + statement + "\033[m"
        if direction == "left":
            self.menuIndex = ((self.menuIndex - 1) % 4)
        elif direction == "right":
            self.menuIndex = ((self.menuIndex + 1) % 4)

    def operateCamera(self):
        print "camera operation"
        if self.cameraProc == None:
            self.cameraProc = subprocess.Popen(["raspistill", "-s"])
        else:
            print "terminate"
            self.cameraProc.kill()
            self.cameraProc = None
    def pinCallback(self, channel):
        value = self.read(constant.READ_ADDR)
        if value in self.operations:
            if value == 33:
                self.scroll("left")
            elif value == 34:
                self.scroll("right")
            elif value == 69:
                self.doLed(0x20)
                self.operateCamera()
            else:
                print self.operations[value]

