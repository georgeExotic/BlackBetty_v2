"""
Blackbetty:
    TOP = 5
    BOTTOM = 6
"""
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep

class limitSwitch:
    def __init__(self,limitPin):
        self.limitPin = limitPin
        GPIO.setmode(GPIO.BCM)  #set GPIO pind mode to BCM
        GPIO.setup(self.limitPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    def getSwitchStatus(self):
        self.status = GPIO.input(self.limitPin)
        return self.status  #true = on // false = off

if __name__ == "__main__":
    home_switch = limitSwitch(6)
    while True:
        print(home_switch.getSwitchStatus())
        sleep(0.1)
