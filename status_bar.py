import tkinter as tk
from tkinter import ttk

class StatusBar(tk.Frame):
    def __init__(self, parent, canvas, width_mm=32, height_mm=32, width_px=400, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Configurable workspace dimensions (in mm)
        self.workspace_width = width_mm
        self.workspace_height = height_mm
        self.pixels_to_mm = self.workspace_width / float(width_px)

        # Create a main content area (just a blank area for cursor tracking)
        self.canvas = canvas
        self.canvas.bind("<Motion>", self.update_cursor_position)  # track cursor movement

        # Create the status bar
        self.grid_columnconfigure(0, weight=1)  # left column stretches
        self.grid_columnconfigure(1, weight=0)  # right column (cursor position)
        self.grid_rowconfigure(0, weight=0)

        # Add items to the status bar
        # Left-aligned workspace label
        self.workspace_label = tk.Label(
            self,
            text=f"{self.workspace_width}mm (W) x {self.workspace_height}mm (H)",
            fg="black",
            anchor="w"
        )
        self.workspace_label.grid(row=0, column=0, sticky="w", padx=(5,5))

        # Right-aligned cursor position label
        self.cursor_label = tk.Label(
            self,
            text="(0.0, 0.0)",  # Default cursor position
            fg="black",
            anchor="e",
            width=8
        )
        self.cursor_label.grid(row=0, column=1, sticky="e", padx=(0,5))

    def update_cursor_position(self, event):
        """Update the cursor position label with current mouse coordinates."""
        x, y = event.x * self.pixels_to_mm, event.y * self.pixels_to_mm
        self.cursor_label.config(text=f"({x:.1f}, {y:.1f})")

# Create the main application window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Status Bar Example")
    root.geometry("400x300")  # Set a default window size
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
