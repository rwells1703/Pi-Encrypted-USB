from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

W, H = (128, 64)

def mount(device):
    print("yay the device is mounted")

def more(device):
    draw_menu(device, more_menu, "More Menu")

def poweroff(device):
    print("nooooo the power is out")
    exit()

def back(device):
    return True

def format_drive(device):
    print("the drive has been factory reset")

def change_fingerprint(device):
    print("new fingerprint please")

def change_card(device):
    print("tap new card please")

def change_master_psk(device):
    print("enter new psk please")

def factory_reset(device):
    print("completely reset")

main_menu = {
    "Mount": mount,
    "More": more,
    "Poweroff": poweroff
}

more_menu = {
    "Format drive": format_drive,
    "Change fingerprint": change_fingerprint,
    "Change card": change_card,
    "Change master psk": change_master_psk,
    "Factory reset": factory_reset,
    "Back": back
}

def centred_text_coords(draw, text):
    w, h = draw.textsize(text)

    return [
        (W-w)/2,
        (H-h)/2
        ]

def draw_centred_text(draw, text, fill="white", x_pos=None, y_pos=None):
    coords = centred_text_coords(draw, text)

    if x_pos != None:
        coords[0] = x_pos
    if y_pos != None:
        coords[1] = y_pos

    draw.text(coords, text, fill)

def draw_menu(device, menu, title):
    selected = 0
    back = False

    while not back:
        with canvas(device) as draw:
            draw_centred_text(draw, title, y_pos=0)
            border = 0
            draw.line((border, 10, W-border, 10), fill="white")

            i = 0
            for entry in menu.keys():
                if i == selected:
                    entry = "> " + entry

                draw_centred_text(draw, entry, x_pos=border, y_pos=(i*8)+14)
                i += 1

        choice = input()

        if choice == "y":
            back = list(menu.values())[selected](device)
        else:
            selected = (selected+1)%len(menu)

def main():
    serial = i2c(port=1, address=0x3C)
    device = sh1106(serial)
    draw_menu(device, main_menu, "Main Menu")

main()