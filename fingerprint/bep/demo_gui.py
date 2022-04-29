#!/usr/bin/env python3

# Copyright (c) 2020 Fingerprint Cards AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""BEP Demo App GUI client """

import sys
try:
    import tkinter as tk
except ImportError:
    sys.exit("This tool requires the tkinter Python module. Install it using:"
             "\n $ sudo apt-get install python3-tk")


class DemoApp(tk.Frame):
    """ Demo App Host Communication GUI """
    # pylint: disable = C0103
    # pylint: disable = R0901
    def __init__(self, master=None, bep_if=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.widgets = {}
        self.create_widgets()
        self.bep_interface = bep_if
        self.fp_image = None
        self.max_progress = None
        self.text_color = "black"

    def create_widgets(self):
        """ Create widgets """
        self.fpc_logo = tk.PhotoImage(file="fpc_logo.png")
        logo = tk.Label(self, image=self.fpc_logo)
        logo.grid(columnspan=2, pady=5)
        self.widgets["logo"] = logo

        button = tk.Button(self, width=25)
        button["text"] = "Delete all templates"
        button["command"] = self.delete_all_templates
        button.grid(row=1, column=0, padx=5)
        self.widgets["delete_template_btn"] = button

        button = tk.Button(self, width=25)
        button["text"] = "Enroll finger"
        button["command"] = self.enroll
        button.grid(row=1, column=1, padx=5)
        self.widgets["enroll_btn"] = button

        button = tk.Button(self, width=25)
        button["text"] = "Capture and identify"
        button["command"] = self.capture_and_identify
        button.grid(row=2, column=0, padx=5)
        self.widgets["capture_and_identify_btn"] = button

        button = tk.Button(self, width=25)
        button["text"] = "Capture and upload image"
        button["command"] = self.capture_and_upload_image
        button.grid(row=2, column=1, padx=5)
        self.widgets["capture_and_extract_image_btn"] = button

        label = tk.Label(self, width=25)
        label["text"] = "Fingerprint image"
        label.grid(row=3, column=0, columnspan=1, pady=5)
        self.widgets["fp_image_lbl"] = label

        label = tk.Label(self, width=25)
        label["text"] = "Histogram"
        label.grid(row=3, column=1, columnspan=1, pady=5)
        self.widgets["fp_image_lbl"] = label

        canvas = tk.Canvas(self, width=200, height=200)
        canvas.create_rectangle(4, 4, 196, 196, fill="white")
        canvas.grid(row=4, column=0, columnspan=1, pady=5)
        self.widgets["fp_canvas"] = canvas

        canvas = tk.Canvas(self, width=256, height=150)
        canvas.create_rectangle(1, 1, 256, 150, fill="white")
        canvas.grid(row=4, column=1, columnspan=1, pady=5, padx=5)
        self.widgets["histo_canvas"] = canvas

        canvas = tk.Canvas(self, width=500, height=32)
        canvas.create_rectangle(1, 1, 500, 32, fill="grey")
        canvas.grid(row=5, columnspan=2)
        self.widgets["pb_canvas"] = canvas

        label = tk.Label(self, width=25)
        label["text"] = "Identify status"
        label.grid(row=6, column=0, pady=5)
        self.widgets["identifystat_lbl"] = label

        canvas = tk.Canvas(self, width=50, height=50)
        canvas.create_oval(1, 1, 50, 50, fill='grey')
        canvas.grid(row=6, column=1, pady=5)
        self.widgets["identifystat_canvas"] = canvas

        listbox = tk.Listbox(self, width=60)
        listbox.grid(row=7, columnspan=2, pady=5)
        self.widgets["log_listbox"] = listbox

    def delete_all_templates(self):
        print("Delete templates")
        success = self.bep_interface.template_remove_all_flash()
        if success:
            self.log("Delete templates finished successfully", "green")
        else:
            self.log("Delete templates failed", "red")
        self.log("")

    def enroll(self):
        print("Enroll finger")
        success = self.bep_interface.enroll(callback=self.command_callback)
        if success:
            self.update_progress(self.max_progress)
            self.log("Enroll finished successfully", "green")
        else:
            self.log("Enroll failed", "red")
        self.log("")

    def capture_and_identify(self):
        print("Capture and identify")
        success = self.bep_interface.identify(callback=self.command_callback)
        if success:
            self.log("Capture and identify finished successfully", "green")
        else:
            self.log("Capture and identify failed", "red")
        self.log("")

    def capture_and_upload_image(self):
        """Capture and upload image"""
        print("Capture and extract image")
        self.max_progress = 160*160
        widget = self.widgets["histo_canvas"]
        widget.delete("all")
        widget.create_rectangle(1, 1, 256, 150, fill="white")
        widget.update_idletasks()
        widget = self.widgets["fp_canvas"]
        widget.delete("all")
        widget.create_rectangle(4, 4, 196, 196, fill="white")
        widget.update_idletasks()

        success = self.bep_interface.image_get(display=False, callback=self.command_callback)[0]
        if success:
            self.fp_image = tk.PhotoImage(file="image.png")
            self.create_histogram(self.fp_image)
            widget.create_image(100, 100, image=self.fp_image)
            self.log("Capture and upload image finished successfully", "green")
        else:
            self.log("Capture and upload image failed", "red")
        self.log("")

    def create_histogram(self, image):
        """Create histogram"""
        colorbin = [0] * 256
        maxnum = 0

        for y in range(image.height()):
            for x in range(image.width()):
                # pixel is a rgb tuple. since it's greyscale we can use any element
                pixelvalue = image.get(x, y)[0]
                colorbin[pixelvalue] += 1
                if colorbin[pixelvalue] > maxnum:
                    maxnum = colorbin[pixelvalue]

        # Set "white" value to next highest to see histogram when sensor is not fully covered
        if colorbin[255] == maxnum:
            maxnum = 0
            for c in range(255):
                if colorbin[c] > maxnum:
                    maxnum = colorbin[c]
            colorbin[255] = maxnum

        # Scale height
        scalefactor = 150 / maxnum

        widget = self.widgets["histo_canvas"]
        for x in range(256):
            widget.create_line(x, 150, x, 150 - colorbin[x] * scalefactor)

    def command_callback(self, text=None, progress=None, max_progress=None, match=None):
        if text:
            self.log(text)
        if progress:
            if max_progress and max_progress > 0:
                self.max_progress = max_progress
            self.update_progress(progress)
        if match is True:
            self.set_identify_state('green')
        elif match is False:
            self.set_identify_state('red')
        else:
            self.set_identify_state('grey')

    def update_progress(self, progress=None):
        widget = self.widgets["pb_canvas"]
        widget.delete("all")
        widget.create_rectangle(1, 1, 500, 32, fill="grey")
        widget.create_rectangle(3, 3, 494 * progress / self.max_progress + 3,
                                30, fill="green")
        widget.update_idletasks()

    def set_identify_state(self, color=None):
        widget = self.widgets["identifystat_canvas"]
        widget.delete("all")
        widget.create_oval(1, 1, 50, 50, fill=color)
        widget.update_idletasks()

    def log(self, text=None, color="black"):
        widget = self.widgets["log_listbox"]
        widget.insert("end", text)
        widget.itemconfig("end", fg=color)
        widget.see("end")
        widget.update_idletasks()
