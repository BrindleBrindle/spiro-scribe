import tkinter as tk
import re


class PreviewCanvas(tk.Canvas):
    """
    A canvas to display circular patterns, translating millimeter units into pixels.
    """

    def __init__(self, parent, width=400, height=400, mm_to_px_ratio=10, *args, **kwargs):
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
        super().__init__(parent, width=width, height=height, bg="#FFFFFF", *args, **kwargs)

        # Store parameters as attributes
        self._width = width
        self._height = height
        self._mm_to_px_ratio = mm_to_px_ratio
        self._set_origin_center()
        self.grid(row=0, column=0, sticky="nsew")

        self.pattern = []
        self.bg_color = "#FFFFFF"
        self.pattern_color = "#000000"
        self.pattern_linewidth = 1

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
                        element['x1'], element['y1'], element['x2'], element['y2'], self.pattern_color, self.pattern_linewidth
                    )

    def _mm_to_px(self, mm):
        """
        Convert millimeters to pixels.

        Arguments:
            mm (float): Amount defined in millimeters.

        Returns:
            Amount defined in pixels.
        """
        return mm * self._mm_to_px_ratio

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

        self.create_line(
            x1_px,
            y1_px,
            x2_px,
            y2_px,
            fill=color,
            width=width
        )

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
