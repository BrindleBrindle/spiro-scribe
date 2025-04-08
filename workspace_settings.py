import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser  # for the color picker
# Gold color: "#FFDB2F"


class WorkspaceSettings(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.spinboxes = {}  # Dictionary to store Spinbox references

        # Row 1: Material diameter
        self.create_label_spinbox(
            row=0,
            label_text="Material diameter (mm)",
            from_=0,
            to=50,
            increment=1,
            default_value=32,
            command=self.on_material_dia_change,
            key="material diameter"
        )

        # Row 2: Border line width
        self.create_label_spinbox(
            row=1,
            label_text="Border line width (px)",
            from_=1,
            to=5,
            increment=1,
            default_value=2,
            command=self.on_border_lw_change,
            key="border lw"
        )

        # Row 3: Pattern line width
        self.create_label_spinbox(
            row=2,
            label_text="Pattern line width (px)",
            from_=1,
            to=5,
            increment=1,
            default_value=1,
            command=self.on_pattern_lw_change,
            key="pattern lw"
        )

        # Row 4: Fill color with color
        self.create_color_picker(row=3, label_text="Fill color", default_color="#FFFFFF")  # set default color

        # Configure grid weights for proper resizing
        self.grid_columnconfigure(0, weight=1)  # Label column
        self.grid_columnconfigure(1, weight=1)  # Spinbox or color picker

    def on_border_lw_change(self):
        pass

    def on_material_dia_change(self):
        pass

    def on_pattern_lw_change(self):
        self.pattern_linewidth = self.spinboxes["pattern lw"].get()
        self.event_generate("<<PatternLinewidthAction>>")  # notify parent of new linewidth

    def create_label_spinbox(self, row, label_text, from_, to, increment, default_value, command, key):
        """
        Create a Label and Spinbox in a row. Store a reference in a dictionary.
        """
        label = ttk.Label(self, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        spinbox = ttk.Spinbox(self, from_=from_, to=to, increment=increment, width=10, command=command)
        spinbox.set(default_value)  # set the default value
        spinbox.grid(row=row, column=1, padx=10, pady=5, sticky="w")

        # Store the Spinbox in the dictionary with a unique key.
        self.spinboxes[key] = spinbox

    def create_color_picker(self, row, label_text, default_color):
        """Helper function to create a Label and a color picker square in a row."""
        label = ttk.Label(self, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        # Create a small square to display the selected color with a subtle border
        self.color_display = tk.Canvas(
            self,
            width=20,
            height=20,
            bg=default_color,  # set to the initial default color
            highlightthickness=1,  # subtle border thickness
            highlightbackground="gray"  # subtle border color
        )
        self.color_display.grid(row=row, column=1, padx=10, pady=5, sticky="w")

        # Store the default color
        self.current_color = default_color

        # Bind a click event to open the color picker
        self.color_display.bind("<Button-1>", self.open_color_picker)

    def open_color_picker(self, event):
        """Open a color picker dialog and update the color display."""
        # Open the color picker with the current color pre-selected
        color_code = colorchooser.askcolor(color=self.current_color, title="Choose a color")[1]  # get the color hex code
        if color_code:  # if a color is selected, update the square's background
            self.current_color = color_code  # store the new color
            self.color_display.config(bg=color_code)
            self.event_generate("<<BackgroundColorAction>>")  # notify parent of new color


# Main application demonstrating how to embed the class in an application.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Workspace Settings")
    root.resizable(False, False)  # prevent resizing in both width and height

    # Embed WorkspaceSettings class inside the main window
    workspace_settings_pane = WorkspaceSettings(root)
    workspace_settings_pane.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # use grid to position the pane

    # Configure grid weights for resizing
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Run the application
    root.mainloop()
