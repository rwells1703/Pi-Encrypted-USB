import time
import RPi.GPIO as GPIO

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

W, H = (128, 64)

class Display():
    def __init__(self):
        self.initialise()

    def initialise(self):
        # Connect to the OLED display over i2c
        self.serial = i2c(port=1, address=0x3C)
        
        # Use the sh1106 driver
        self.device = sh1106(self.serial)

        # Define the input buttons and their GPIO pins
        self.buttons = {
            "top": {"gpio": 16, "pressed": False},
            "bottom": {"gpio": 12, "pressed": False}
            }

        # Prevent warnings if the GPIO pin roles have already been set previously
        GPIO.setwarnings(False)

        # Set the GPIO pin numbering mode to BCM
        GPIO.setmode(GPIO.BCM)

        # Set the GPIO pins connecting the buttons to pull up
        for button in self.buttons.values():
            GPIO.setup(button["gpio"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def centred_text_coords(self, draw, text):
        w, h = draw.textsize(text)

        return [
            (W-w)/2,
            (H-h)/2
            ]

    def draw_centred_text(self, draw, text, fill="white", x_pos=None, y_pos=None):
        coords = self.centred_text_coords(draw, text)

        if x_pos != None:
            coords[0] = x_pos
        if y_pos != None:
            coords[1] = y_pos
        
        draw.text(coords, text, fill)
    

    def draw_menu(self, menu, title):
        selected = 0
        back = False

        while not back:
            with canvas(self.device) as draw:
                self.draw_centred_text(draw, title, y_pos=0)
                border = 0
                draw.line((border, 10, W-border, 10), fill="white")

                i = 0
                for entry in menu.keys():
                    if i == selected:
                        entry = "> " + entry

                    self.draw_centred_text(draw, entry, x_pos=border, y_pos=(i*8)+14)
                    i += 1

            self.poll_buttons()

            if self.buttons["top"]["pressed"]:
                selected = (selected+1)%len(menu)
            elif self.buttons["bottom"]["pressed"]:
                back = list(menu.values())[selected]()

            time.sleep(0.01)
    
    def poll_buttons(self):
        for button in self.buttons.values():
            if not GPIO.input(button["gpio"]):
                button["pressed"] = True
            else:
                button["pressed"] = False

    def draw_message(self, message):
        with canvas(self.device) as draw:
            self.draw_centred_text(draw, message)
    
    def wait_for_button(self):
        input()

    def draw_input_prompt(self, input_name):
        with canvas(self.device) as draw:
            pass