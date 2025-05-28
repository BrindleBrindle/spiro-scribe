import tkinter as tk
import numpy as np
import re
import math
from fractions import Fraction


class PreviewCanvas(tk.Canvas):
    """
    A canvas to display circular patterns, translating millimeter units into pixels.
    """

    def __init__(self, parent, width=400, height=400, mm_to_px_ratio=15, *args, **kwargs):
        """
        Initialize the PreviewCanvas object.

        Arguments:
            parent: Parent tkinter widget.
            width (int): Width of the canvas in px.
            height (int): Height the canvas in px.
            mm_to_px_ratio (float): Multiplier for conversion from millimeters to pixels.

        Returns:
            None
        """
        super().__init__(parent, width=width, height=height, *args, **kwargs)

        # Store parameters as attributes
        self._width = width
        self._height = height
        self._mm_to_px_ratio = mm_to_px_ratio
        self._set_origin_center()

        # Pattern settings
        self.pattern = []
        self.pattern_color = "#000000"
        self.pattern_linewidth = 1

        # Workspace settings
        self.bg_color = "#FFFF80"
        self.show_origin = True
        self.origin_position = (1, 1)  # center

    def _set_origin_center(self):
        self._origin_x = self._width / 2
        self._origin_y = self._height / 2

    def set_bg_color(self, color):
        if not self._valid_color(color):
            raise ValueError("Fill color must be a valid 3- to 6-character hex color (\"#FFF\" or \"#FFFFFF\").")
            return
        self.bg_color = color

    def set_pattern_linewidth(self, width):
        if not self._valid_linewidth(width):
            raise ValueError("Pattern linewidth must be a positive integer between 1 to 10.")
            return
        self.pattern_linewidth = width

    def set_pattern(self, pattern):
        """
        Render multiple items on the canvas at once.

        Arguments
            pattern (list): List of drawing elements defined in millimeters.
                            Each element must be a circle or line:
                            {'type': 'circle', 'x': <val>, 'y': <val>, 'radius': <val>}
                            {'type': 'line', 'x1': <val>, 'y1': <val>, 'x2': <val>, 'y2': <val>}

            color (str):    Line display color as string ("#FFF" or "#FFFFFF").
            width (int):    Line display width in pixels.

        Returns:
            None
        """
        self.pattern = pattern

    def refresh_pattern(self):
        self.config(bg=self.bg_color)  # Set background color
        self.delete("all")  # Clear the canvas

        # Iterate through all elements in the pattern
        if self.pattern:
            for element in self.pattern:
                if element['type'] == 'circle':
                    self._draw_circle(
                        element['x'], element['y'], element['radius'], self.pattern_color, self.pattern_linewidth
                    )
                elif element['type'] == 'line':
                    self._draw_line(
                        element['x1'], element['y1'], element['x2'], element['y2'],
                        self.pattern_color, self.pattern_linewidth
                    )
                elif element['type'] == 'roulette':
                    self._draw_roulette(
                        element['R'], element['r'], element['s'], element['d'],
                        element['display res'], self.pattern_color, self.pattern_linewidth
                    )

        # Draw crosshair
        if self.show_origin:
            self._draw_crosshair(self.origin_position)

    def _mm_to_px(self, mm):
        """
        Convert millimeters to pixels.

        Arguments:
            mm (float): Amount defined in millimeters.

        Returns:
            Amount defined in pixels.
        """
        return mm * self._mm_to_px_ratio

    def _draw_crosshair(self, position):
        """
        Draw a red crosshair on the canvas based on a 3x3 matrix position.

        Arguments:
            position (tuple): A tuple (i, j) where:
                              i - the row index (0 to 2),
                              j - the column index (0 to 2).
        Returns;
            None
        """
        # Clear the canvas before drawing the crosshair
        self.delete("crosshair")

        # Get the canvas width and height
        canvas_width = self._width
        canvas_height = self._height

        # Ensure the position is valid
        if not (0 <= position[0] <= 2 and 0 <= position[1] <= 2):
            raise ValueError("Invalid position. Both i and j must be in the range 0 to 2.")

        # Define the crosshair center positions
        N_L = 2  # nudge crosshair N pixels from left edge
        N_R = -1  # nudge crosshair N pixels from right edge
        N_T = 2  # nudge crosshair N pixels from top edge
        N_B = -1  # nudge crosshair N pixels from bottom edge
        centers = {
            (0, 0): (N_L, N_T),                                 # top-left
            (0, 1): (canvas_width / 2, N_T),                    # top-middle
            (0, 2): (canvas_width - N_R, N_T),                  # top-right
            (1, 0): (N_L, canvas_height / 2),                   # center-left
            (1, 1): (canvas_width / 2, canvas_height / 2),      # center
            (1, 2): (canvas_width - N_R, canvas_height / 2),    # center-right
            (2, 0): (N_L, canvas_height - N_B),                 # bottom-left
            (2, 1): (canvas_width / 2, canvas_height - N_B),    # bottom-middle
            (2, 2): (canvas_width - N_R, canvas_height - N_B),  # bottom-right
        }

        # Get the (x, y) coordinates for the specified position
        x, y = centers[position]

        # Draw horizontal line
        self.create_line(x - 10, y, x + 10, y, fill="red", width=3, tags="crosshair")

        # Draw vertical line
        self.create_line(x, y - 10, x, y + 10, fill="red", width=3, tags="crosshair")

    def _draw_roulette(self, R, r, s, d, display_res, color, width):
        """
        Render a roulette on the canvas.

        Arguments:
            R (float): Radius of the fixed circle.
            r (float): Radius of the rolling circle.
            s (int): Scaling factor for the rolling circle radius, either -1 or 1.
            d (float): Distance of the pen point from the rolling circle center.
            display_res (int): Resolution of the curve (number of points).
            color (str): The display color of the line (#FFF or #FFFFFF).
            width (int): The display width of the line in px.

        Returns:
            None
        """
        def compute_point(theta):
            """Helper function to compute the (x, y) point for a given theta."""
            factor = (R + s * r)
            x = factor * np.cos(theta) - s * d * np.cos(theta * factor / r)
            y = factor * np.sin(theta) - d * np.sin(theta * factor / r)
            return x, y

        # Define R and r as Fractions
        R = Fraction(R)
        r = Fraction(r)

        # Compute the effective radius
        effective_R = R + s * r

        # Compute the GCD of the numerators and denominators
        numerator_gcd = math.gcd(r.numerator, effective_R.numerator)
        denominator_lcm = (r.denominator * effective_R.denominator) // math.gcd(r.denominator, effective_R.denominator)

        # Simplify the GCD as a fraction
        gcd_fraction = Fraction(numerator_gcd, denominator_lcm)

        # Calculate the number of turns needed to close the path.
        n_turns = r / gcd_fraction
        total_angle = n_turns * 2 * np.pi
        thetas = np.linspace(0, total_angle, display_res, endpoint=False)

        # Compute the starting point.
        first_x, first_y = compute_point(thetas[0])
        start_x, start_y = first_x, first_y

        # Draw the curve by connecting consecutive points.
        for theta in thetas[1:]:
            end_x, end_y = compute_point(theta)
            self._draw_line(start_x, start_y, end_x, end_y, color, width)
            start_x, start_y = end_x, end_y

        # Close the loop by connecting the last point to the first point.
        self._draw_line(start_x, start_y, first_x, first_y, color, width)

    def _draw_line(self, x1, y1, x2, y2, color, width):
        """
        Render a line on the canvas.

        Arguments:
            x1 (float): The x-coordinate of the line's start point in mm.
            y1 (float): The y-coordinate of the line's start point in mm.
            x2 (float): The x-coordinate of the line's end point in mm.
            y2 (float): The y-coordinate of the line's end point in mm.
            color (str): The display color of the line (#FFF or #FFFFFF).
            width (int): The display width of the line in px.

        Returns:
            None
        """
        x1_px = self._origin_x + self._mm_to_px(x1)
        y1_px = self._origin_y - self._mm_to_px(y1)
        x2_px = self._origin_x + self._mm_to_px(x2)
        y2_px = self._origin_y - self._mm_to_px(y2)

        self.create_line(x1_px, y1_px, x2_px, y2_px, fill=color, width=width)

    def _draw_circle(self, x, y, radius, color, width):
        """
        Render a circle on the canvas.

        Arguments:
            x (float): The x-coordinate of the circle's center in mm.
            y (float): The y-coordinate of the circle's center in mm.
            radius (float): The radius of the circle in mm.
            color (str): The display color of the circle boundary (#FFF or #FFFFFF).
            width (int): The display width of the circle boundary in px.

        Returns:
            None
        """
        x_px = self._origin_x + self._mm_to_px(x)
        y_px = self._origin_y - self._mm_to_px(y)
        r_px = self._mm_to_px(radius)

        # Draw the circle with a border
        self.create_oval(
            x_px - r_px,
            y_px - r_px,
            x_px + r_px,
            y_px + r_px,
            outline=color,
            width=width
        )

    def _valid_color(self, color):
        """
        Determine if the provided string is a valid hex color. A valid string
        contains a # symbol followed by 3 or 6 hex chars (#FFF or #FFFFFF).

        Arguments:
            color (str): Color string to validate.

        Returns:
            True if valid; otherwise, False.

        """
        pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
        return bool(re.match(pattern, color))

    def _valid_linewidth(self, lw):
        """
        Determine if the provided linewidth is valid.

        Arguments:
            lw (int): Linewidth defined in px.

        Returns:
            True if valid; otherwise, False.
        """
        return isinstance(lw, int) and 1 <= lw <= 10

    # Properties for controlled access to attributes
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value <= 0:
            raise ValueError("Canvas width must be a positive value.")
        self._width = value
        self._set_origin_center()
        self.config(width=self._width)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value <= 0:
            raise ValueError("Canvas height must be a positive value.")
        self._height = value
        self._set_origin_center()
        self.config(width=self._height)


# Main application demonstrating how to embed the class in an application.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Preview Canvas")
    root.resizable(False, False)  # prevent resizing in both width and height

    # Configure grid weights for resizing
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Embed PreviewCanvas class inside the main window with custom parameters
    canvas = PreviewCanvas(
        parent=root,
        width=500,
        height=400,
        mm_to_px_ratio=15,
    )
    canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Demonstrate drawing on the canvas.
    input("Press Enter to draw on the canvas...")
    elements = [{'type': 'circle', 'x': 0, 'y': 0, 'radius': 5}]
    canvas.draw_pattern(elements)

    # Example of updating properties after instantiation.
    input("Press Enter to demonstrate dynamic update of canvas properties...")
    canvas.width = 600  # Resize the canvas
    canvas.draw_pattern(elements)

    # Run the application
    root.mainloop()
