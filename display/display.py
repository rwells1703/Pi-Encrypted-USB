from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

W, H = (128, 64)

class Display():
    def __init__(self):
        self.initialise()

    def initialise(self):
        self.serial = i2c(port=1, address=0x3C)
        self.device = sh1106(self.serial)

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

            choice = input()

            if choice == "y":
                back = list(menu.values())[selected](self.device)
            else:
                selected = (selected+1)%len(menu)

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