# raspberry pi control panel script
# button presses and knob turns perform actions

from smbus2 import SMBusWrapper
import uuid
import time
import RPi.GPIO as GPIO
import atexit
import constant
import subprocess


class PanelController:

    def __init__(self):
        # the camera subprocess variable
        self.camera_process = None

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

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(constant.DETECT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(constant.RESET, GPIO.OUT)

        # watches int pin event 
        GPIO.add_event_detect(constant.DETECT, GPIO.BOTH, callback=self.pin_callback)
        
        self.display_menu()

    @atexit.register
    def reset_board(self):
        GPIO.output(constant.RESET, GPIO.LOW)
        GPIO.output(constant.RESET, GPIO.HIGH)
        GPIO.output(constant.RESET, GPIO.LOW)
        GPIO.cleanup()
        print "Goodbye"

    def keep_alive(self):
        while True:
            time.sleep(3)

    def read(self, address):
        b = None
        with SMBusWrapper(1) as bus:
            try:
                b = bus.read_byte_data(constant.DEVICE_ADDR, address, False)
            except IOError:
                b = 0
            return b

    def change_led_state(self, led):
        pwm = self.read(led)
        with SMBusWrapper(1) as bus:
            if pwm == constant.PWM_LOW:
                bus.write_byte_data(constant.DEVICE_ADDR, led, constant.PWM_HIGH)
            else:
                bus.write_byte_data(constant.DEVICE_ADDR, led, constant.PWM_LOW)

    def turn_off_all_leds(self):
        with SMBusWrapper(1) as bus:
            bus.write_byte_data(constant.DEVICE_ADDR, constant.GREEN_LED, constant.PWM_LOW)
            bus.write_byte_data(constant.DEVICE_ADDR, constant.RED_LED, constant.PWM_LOW)

    def scroll(self, direction):
        # prevent action during camera operation
        if self.camera_process is not None:
            return

        # clear the terminal
        subprocess.call('clear', shell=True)

        if direction == "left":
            self.menuIndex = ((self.menuIndex - 1) % 4)
        elif direction == "right":
            self.menuIndex = ((self.menuIndex + 1) % 4)
            
        self.display_menu()

    def display_menu(self):
        statement = self.menuOptions[self.menuIndex]
        for option in self.menuOptions:
            if option == statement:
                print "\033[44;33m" + statement + "\033[m"
            else:
                print option
                
    def toggle_camera(self):
        # toggle on
        if self.camera_process is None:
            if self.menuIndex == 0:
                self.change_led_state(constant.GREEN_LED)
                proc = ["raspistill", "-s","-dt", "-o", "photos/img%04d.jpg"] 
                self.camera_process = subprocess.Popen(proc)
            elif self.menuIndex == 1:
                filename = uuid.uuid4()
                filepath = "video/{}.h264".format(filename)
                proc = ["raspivid", "-t", "0", "-s", "-o", filepath, "-i", "pause"] 
                self.camera_process = subprocess.Popen(proc)
            elif self.menuIndex == 3:
                print "GoodBye"
                subprocess.call(["shutdown", "-h", "now"])
        else:
            # toggle off
            self.turn_off_all_leds()
            self.camera_process.kill()
            self.camera_process = None
    
    def take_photo(self):
        if self.camera_process is not None:
            # send signal to camera operation
            self.camera_process.send_signal(constant.CAMERA_SIGNAL)
            
            # when camera operation is video, use red LED to notate recording
            if self.menuIndex == 1:
                self.change_led_state(constant.RED_LED)
        else:
            print "Toggle Camera First"

    def pin_callback(self, channel):
        value = self.read(constant.READ_ADDR)
        if value in self.operations:
            if value == 33:
                self.scroll("left")
            elif value == 34:
                self.scroll("right")
            elif value == 65:
                self.toggle_camera()
            elif value == 69:
                self.take_photo()
            elif value == 77:
                statement = self.menuOptions[self.menuIndex] 
                print "\033[44;33m" + statement + "\033[m"
                print self.menuIndex
            else:
                print self.operations[value]
