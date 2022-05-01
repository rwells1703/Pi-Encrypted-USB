import RPi.GPIO as GPIO

def configure_gpio():
    # Prevent warnings if the GPIO pin roles have already been set previously
    GPIO.setwarnings(False)

    # Set the GPIO pin numbering mode to BCM
    GPIO.setmode(GPIO.BCM)

class Button:
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin

        # Set the GPIO pin connecting the button to pull up
        GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.pressed = False

    def is_pressed(self):
        if not GPIO.input(self.gpio_pin):
            if not self.pressed:
                self.pressed = True
                return True
        else:
            self.pressed = False
            return False
