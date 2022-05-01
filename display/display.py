import time
import PIL

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

import display.button

W, H = (128, 64)

class Display():
    def __init__(self):
        self.start()

    def start(self):
        # Connect to the OLED display over i2c
        self.serial = i2c(port=1, address=0x3C)
        
        # Use the sh1106 driver
        self.device = sh1106(self.serial)

        display.button.configure_gpio()

        # Define the input buttons and their GPIO pins
        self.buttons = {
            "top": display.button.Button(16),
            "bottom": display.button.Button(12)
            }

    def stop(self):
        self.device.cleanup()

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
        
        font = PIL.ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        draw.text(coords, text, fill, font)
    

    def draw_menu(self, menu, title):
        selected = 0
        update_display = True

        while True:
            if update_display:
                update_display = False
                with canvas(self.device) as draw:
                    self.draw_centred_text(draw, title, y_pos=0)
                    border = 0
                    draw.line((border, 14, W-border, 14), fill="white")

                    i = 0
                    for entry in menu.keys():
                        if i == selected:
                            entry = "> " + entry

                        self.draw_centred_text(draw, entry, x_pos=border, y_pos=(i*12)+14)
                        i += 1

            if self.buttons["top"].is_pressed():
                selected = (selected+1)%len(menu)
                update_display = True
            elif self.buttons["bottom"].is_pressed():
                list(menu.values())[selected]()
                update_display = True

            time.sleep(0.01)

    def draw_message(self, message):
        with canvas(self.device) as draw:
            self.draw_centred_text(draw, message)
    
    def wait_for_button(self):
        input()

    def draw_input_prompt(self, input_name):
        with canvas(self.device) as draw:
            pass