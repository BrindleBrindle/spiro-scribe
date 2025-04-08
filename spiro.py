import tkinter as tk
import random
import numpy as np
from user_controls import UserControlsPane
from preview_canvas import PreviewCanvas
from post_processor import GCodePostProcessor


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
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = PreviewCanvas(
            parent=self.frame,
            width=400,
            height=400,
            mm_to_px_ratio=15,
        )
        self.canvas.grid(row=0, column=0, padx=(5, 5), pady=(5, 0), sticky="nsew")

        self.user_controls = UserControlsPane(self.frame)
        self.user_controls.grid(row=1, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.post_processor = GCodePostProcessor()
        self.circles = []

        # Bind to widget custom events
        self.bind("<<BackgroundColorAction>>", self.handle_background_color_event)
        self.bind("<<PatternLinewidthAction>>", self.handle_pattern_lw_event)
        self.bind("<<UpdateCircleAction>>", self.handle_update_circle_event)

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

    def generate_random_circles(self):
        """
        Generate a random number of circles (between 3 and 12) in a circular pattern.

        Arguments:
            None

        Returns:
            list (Dict): A list of drawing elements defined in mm.
        """
        num_circles = random.randint(3, 20)
        circles = []

        radius = 6  # mm
        angles = np.linspace(0, 2 * np.pi, num_circles, endpoint=False)

        for theta in angles:
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            circles.append({'type': 'circle', 'x': x, 'y': y, 'radius': radius})

        return circles


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
