import time
import PIL

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

import display.button

W, H = (128, 64)
FONT_SIZE = 12

class Display():
    def __init__(self):
        self.start()

    def start(self):
        # Connect to the OLED display over i2c
        self.serial = i2c(port=1, address=0x3C)
        
        # Use the sh1106 driver
        self.device = sh1106(self.serial)

        self.font = PIL.ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONT_SIZE)

        display.button.configure_gpio()

        # Define the input buttons and their GPIO pins
        self.buttons = {
            "top": display.button.Button(16),
            "bottom": display.button.Button(12)
            }

    def stop(self):
        self.device.cleanup()

    def centred_text_coords(self, draw, text):
        w, h = draw.textsize(text, self.font)

        return [
            (W-w)/2,
            (H-h)/2
            ]

    def draw_centred_text(self, draw, text, x_pos=None, y_pos=None, x_offset=0, y_offset=0, fill="white"):
        coords = self.centred_text_coords(draw, text)

        if x_pos != None:
            coords[0] = x_pos
        if y_pos != None:
            coords[1] = y_pos

        coords[0] += x_offset
        coords[1] += y_offset

        draw.text(coords, text, fill, self.font)
    

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

                        self.draw_centred_text(draw, entry, x_pos=border, y_pos=(i*FONT_SIZE) + 2 + FONT_SIZE)
                        i += 1

            if self.buttons["top"].is_pressed():
                selected = (selected+1)%len(menu)
                update_display = True
            elif self.buttons["bottom"].is_pressed():
                list(menu.values())[selected]()
                update_display = True

            time.sleep(0.01)

    def draw_message(self, message):
        messages = message.split("\n")

        with canvas(self.device) as draw:
            line = 0
            for message in messages:
                if (len(messages) > 1):
                    y_offset=FONT_SIZE*(line-len(messages)/2+1)
                else:
                    y_offset = 0

                self.draw_centred_text(draw, message, y_offset=y_offset)
                line += 1
    
    def wait_for_button(self):
        input()

    def draw_input_prompt(self, input_name):
        with canvas(self.device) as draw:
            pass