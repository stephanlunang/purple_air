import time

import RPi.GPIO as GPIO


class LEDs:
    def __init__(self):
        self.state = [0, 0, 0]
        self.green_gpio = 2
        self.yellow_gpio = 3
        self.red_gpio = 4

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.green_gpio, GPIO.OUT)
        GPIO.setup(self.yellow_gpio, GPIO.OUT)
        GPIO.setup(self.red_gpio, GPIO.OUT)

    def green_only(self):
        GPIO.output(self.green_gpio, GPIO.HIGH)
        GPIO.output(self.yellow_gpio, GPIO.LOW)
        GPIO.output(self.red_gpio, GPIO.LOW)

    def yellow_only(self):
        GPIO.output(self.green_gpio, GPIO.LOW)
        GPIO.output(self.yellow_gpio, GPIO.HIGH)
        GPIO.output(self.red_gpio, GPIO.LOW)

    def red_only(self):
        GPIO.output(self.green_gpio, GPIO.LOW)
        GPIO.output(self.yellow_gpio, GPIO.LOW)
        GPIO.output(self.red_gpio, GPIO.HIGH)

    def yellow_green(self):
        GPIO.output(self.green_gpio, GPIO.HIGH)
        GPIO.output(self.yellow_gpio, GPIO.HIGH)
        GPIO.output(self.red_gpio, GPIO.LOW)

    def red_yellow(self):
        GPIO.output(self.green_gpio, GPIO.LOW)
        GPIO.output(self.yellow_gpio, GPIO.LOW)
        GPIO.output(self.red_gpio, GPIO.HIGH)

    def all_off(self):
        GPIO.output(self.green_gpio, GPIO.HIGH)
        GPIO.output(self.yellow_gpio, GPIO.HIGH)
        GPIO.output(self.red_gpio, GPIO.HIGH)
        time.sleep(.3)
        GPIO.output(self.green_gpio, GPIO.LOW)
        GPIO.output(self.yellow_gpio, GPIO.LOW)
        GPIO.output(self.red_gpio, GPIO.LOW)
