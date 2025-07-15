import tkinter as tk


class StatusBar(tk.Frame):
    def __init__(self, parent, canvas, width_mm=32, width_px=400, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Configurable workspace dimensions
        self.width_mm = width_mm
        self.height_mm = width_mm
        self.width_px = width_px
        self.height_px = width_px
        self.pixels_to_mm = self.width_mm / float(self.width_px)

        # Create a main content area (just a blank area for cursor tracking)
        self.canvas = canvas
        self.origin_position = canvas.origin_position
        self.cursor_mapping = self.create_cursor_mapping()
        self.canvas.bind("<Motion>", self.update_cursor_position)  # track cursor movement

        # Create the status bar
        self.grid_columnconfigure(0, weight=1)  # left column stretches
        self.grid_columnconfigure(1, weight=0)  # right column (cursor position)
        self.grid_rowconfigure(0, weight=0)

        # Add items to the status bar
        # Left-aligned workspace label
        self.workspace_label = tk.Label(
            self,
            text=f"{self.width_mm}mm (W) x {self.height_mm}mm (H)",
            fg="black",
            anchor="w"
        )
        self.workspace_label.grid(row=0, column=0, sticky="w", padx=(5, 5))

        # Right-aligned cursor position label
        self.cursor_label = tk.Label(
            self,
            text="(0.0, 0.0)",  # Default cursor position
            fg="black",
            anchor="e",
            width=10
        )
        self.cursor_label.grid(row=0, column=1, sticky="e", padx=(0, 5))

    def create_cursor_mapping(self):
        return {(0, 0): (1, -1, 0, 0),                                          # top-left
                (0, 1): (1, -1, -self.width_px / 2.0, 0),                       # top-middle
                (0, 2): (1, -1, -self.width_px, 0),                             # top-right
                (1, 0): (1, -1, 0, self.height_px / 2.0),                       # center-left
                (1, 1): (1, -1, -self.width_px / 2.0, self.height_px / 2.0),    # center
                (1, 2): (1, -1, -self.width_px, self.height_px / 2.0),          # center-right
                (2, 0): (1, -1, 0, self.height_px),                             # bottom-left
                (2, 1): (1, -1, -self.width_px / 2.0, self.height_px),          # bottom-middle
                (2, 2): (1, -1, -self.width_px, self.height_px)                 # bottom-right
                }

    def update_workspace_size(self, workspace_size):
        """Update the workspace size in mm."""
        self.width_mm = workspace_size
        self.height_mm = workspace_size
        self.pixels_to_mm = self.width_mm / float(self.width_px)

    def update_cursor_position(self, event):
        """Update the cursor position label with current mouse coordinates."""

        # Retrieve direction and offset parameters based on the currently-selected origin.
        kx = self.cursor_mapping[self.origin_position][0]
        ky = self.cursor_mapping[self.origin_position][1]
        dx = self.cursor_mapping[self.origin_position][2]
        dy = self.cursor_mapping[self.origin_position][3]

        # Get the current pixel position of the cursor.
        # Ensure it does not exceed the bounds of the canvas.
        canvas_x = max(0, min(event.x, self.width_px))
        canvas_y = max(0, min(event.y, self.height_px))

        # Calculate the current XY position.
        # Convert pixel position w.r.t canvas to mm position w.r.t. current workpiece origin.
        x = self.pixels_to_mm * (kx * canvas_x + dx)
        y = self.pixels_to_mm * (ky * canvas_y + dy)

        # Update status bar label. Display one decimal place.
        self.cursor_label.config(text=f"({x:.1f}, {y:.1f})")


# Create the main application window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Status Bar Example")
    root.geometry("400x300")  # set a default window size
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    test_canvas = tk.Canvas(root, bg="CadetBlue1")
    test_canvas.grid(row=0, column=0, sticky="nsew")

    width_mm = 32
    height_mm = 32
    width_px = 400

    status_bar = StatusBar(root, canvas=test_canvas, width_mm=width_mm, height_mm=height_mm, width_px=width_px)
    status_bar.grid(row=1, column=0, sticky="nsew")
    root.mainloop()
