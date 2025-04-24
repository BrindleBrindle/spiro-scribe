import tkinter as tk
import random
import math
import numpy as np
from user_controls import UserControlsPane
from preview_canvas import PreviewCanvas
from post_processor import GCodePostProcessor
from settings_dialog import SettingsDialog
from info_dialog import InfoDialog
from status_bar import StatusBar
from PIL import Image, ImageTk


class SpiroScribeApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        """
        Initialize the SpiroScribeApp.

        Arguments:
            None

        Returns:
            None
        """
        super().__init__(*args, **kwargs)  # pass arguments to tk.Tk

        self.title("SpiroScribe")
        self.resizable(False, False)  # prevent resizing in both width and height

        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.menu_frame = tk.Frame(self.frame)
        self.menu_frame.grid_columnconfigure(0, weight=0)
        self.menu_frame.grid_columnconfigure(1, weight=0)
        self.menu_frame.grid_columnconfigure(2, weight=1)
        self.menu_frame.grid_columnconfigure(3, weight=0)
        self.menu_frame.grid(row=0, column=0, padx=(10, 10), pady=(5, 5), sticky="nsew")

        self.export_svg_button = tk.Button(self.menu_frame, text="Export to SVG", command=self.open_export_svg_dialog)
        self.export_svg_button.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

        self.export_gcode_button = tk.Button(self.menu_frame, text="Export to G Code", command=self.open_export_gcode_dialog)
        self.export_gcode_button.grid(row=0, column=1, padx=(5, 5), sticky="nsew")

        self.settings_button = tk.Button(self.menu_frame, text="Settings", command=self.open_settings_dialog)
        self.settings_button.grid(row=0, column=2, padx=(5, 5), sticky="nsw")

        image = Image.open("info.png")
        resized_image = image.resize((24, 24))  # resize to fit the button
        button_image = ImageTk.PhotoImage(resized_image)
        self.info_button = tk.Button(self.menu_frame, image=button_image, command=self.open_info_dialog)
        self.info_button.grid(row=0, column=3, padx=(5, 0), sticky="e")

        # Keep a reference to the image to prevent garbage collection
        self.info_button.image = button_image

        self.canvas = PreviewCanvas(
            parent=self.frame,
            width=400,
            height=400,
            mm_to_px_ratio=15,
        )
        # self.canvas.grid_propagate(False)
        self.canvas.grid(row=1, column=0, padx=(5, 5), pady=(0, 0))

        self.status_bar = StatusBar(self.frame, self.canvas, width_mm=32, height_mm=32, width_px=400)
        self.status_bar.grid(row=2, column=0, padx=(6, 6), sticky="ew")

        self.user_controls = UserControlsPane(self.frame)
        self.user_controls.grid(row=3, column=0, padx=(5, 5), pady=(10, 5), sticky="nsew")
        self.post_processor = GCodePostProcessor()
        self.circles = []

        # Bind to widget custom events
        self.bind("<<BackgroundColorAction>>", self.handle_background_color_event)
        self.bind("<<PatternLinewidthAction>>", self.handle_pattern_lw_event)
        self.bind("<<UpdateCircleAction>>", self.handle_update_circle_event)
        self.bind("<<UpdateRouletteAction>>", self.handle_update_roulette_event)

        self.canvas.refresh_pattern()

    def open_export_svg_dialog(self):
        pass

    def open_export_gcode_dialog(self):
        pass

    def open_settings_dialog(self):
        # Pass in initial values for the dialog
        dialog = SettingsDialog(self,
                                initial_color=self.canvas.bg_color,
                                show_origin=self.canvas.show_origin,
                                origin_position=self.canvas.origin_position
                                )
        settings = dialog.get_settings()
        self.canvas.set_bg_color(settings['bg_color'])
        self.canvas.show_origin = settings['show_origin']
        self.canvas.origin_position = settings['origin_position']
        self.canvas.refresh_pattern()

    def open_info_dialog(self):
        text_list = [
            "A Celebration of Love and Friendship",  # heading
            "This application was created in the spring of 2025 to engrave party favors for the wedding of A. Brindle and N. Saxena."
            ]
        dialog = InfoDialog(self, text_list)

    def handle_background_color_event(self, event):
        """
        Set the background color of the workspace in response to a
        <<BackgroundColorAction>> event triggered by the workspace color picker.
        """
        # Access the data attached to the event
        self.canvas.set_bg_color(event.widget.current_color)
        self.canvas.refresh_pattern()

    def handle_pattern_lw_event(self, event):
        """
        Redraw the pattern on the canvas in response to a <<PatternLinewidthAction>>
        event triggered by the pattern linewidth spinbox. Use the new linewidth.
        """
        self.canvas.set_pattern_linewidth(int(event.widget.pattern_linewidth))
        self.canvas.refresh_pattern()

    def handle_update_circle_event(self, event):
        """
        Redraw the pattern on the canvas in response to a <<UpdateCircleAction>>
        event triggered by the widgets on the Circle Settings tab.
        """
        self.circles = event.widget.get_ring_data()
        self.canvas.set_pattern(self.circles)
        self.canvas.refresh_pattern()

    def handle_update_roulette_event(self, event):
        """
        Redraw the pattern on the canvas in response to a <<UpdateRouletteAction>>
        event triggered by the widgets on the Roulette Settings tab.
        """
        self.roulette = event.widget.get_roulette_data()
        self.canvas.set_pattern(self.roulette)
        self.canvas.refresh_pattern()

    def generate_random_spiro(self):
        pattern = []

        # Determine shape parameters.
        R = random.randint(3, 6)   # radius of circle A (static)
        r = random.randint(1, 6)    # radius of circle B (rolling)
        s = random.choice([-1, 1])  # if s=1, B rolls on outside; if s=-1, B rolls on inside
        d = random.randint(1, 6)   # pen distance from center of circle B
        res = 200                   # resolution: number of linear segments per closed path

        # Calculate number of turns needed to close path
        n_turns = r / float(math.gcd(r, R + s * r))

        points = []
        for theta in np.arange(0, n_turns * 2 * np.pi, n_turns * 2 * np.pi / float(res)):
            x = (R + s * r) * np.cos(theta) - s * d * np.cos(theta * (R + s * r) / float(r))
            y = (R + s * r) * np.sin(theta) - d * np.sin(theta * (R + s * r) / float(r))
            points.append((x, y))

        pattern.append({'type': 'spiro', 'points': points})
        return pattern

    def generate_random_circles(self):
        """
        Generate a random number of circles (between 3 and 12) in a circular pattern.

        Arguments:
            None

        Returns:
            list (Dict): A list of drawing elements defined in mm.
        """
        pattern = []
        num_circles = random.randint(3, 20)

        radius = 6  # mm
        angles = np.linspace(0, 2 * np.pi, num_circles, endpoint=False)

        for theta in angles:
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            pattern.append({'type': 'circle', 'x': x, 'y': y, 'radius': radius})

        return pattern


def center_window(window):
    """
    Center a tkinter window on the screen.

    Arguments:
        window (tk.Tk): The tkinter window to center.

    Returns:
        None
    """
    # Get most up-to-date attribute info
    window.update_idletasks()

    # Get the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the position to center the window
    size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
    x = screen_width / 2 - size[0] / 2
    y = screen_height / 2 - size[1] / 2

    # Set the geometry of the window
    window.geometry("+%d+%d" % (x, y))


# Main execution
if __name__ == "__main__":
    # Set up tkinter window
    app = SpiroScribeApp()

    # Center the window on the screen
    center_window(app)

    # Run the tkinter main loop
    app.mainloop()
