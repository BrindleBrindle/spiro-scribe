import tkinter as tk
import numpy as np


class CircleSettings(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Column and row headings
        column_headings = ["", "Enable", "Ring Diameter", "Circle Diameter", "# Circles"]
        row_headings = ["Ring 1", "Ring 2", "Ring 3"]

        # Create table headers
        for col, heading in enumerate(column_headings):  # The first column is for row headings
            label = tk.Label(self, text=heading)
            label.grid(row=0, column=col, padx=5, pady=5)

        # Create the table rows
        self.widgets = []  # Store widget references for later use
        for row, row_heading in enumerate(row_headings, start=1):
            # Row heading
            label = tk.Label(self, text=row_heading)
            label.grid(row=row, column=0, padx=5, pady=5, sticky="w")

            # Widgets for each column in the row
            row_widgets = []

            # Checkbutton for "Enable"
            enable_var = tk.BooleanVar(value=False)
            checkbutton = tk.Checkbutton(self, variable=enable_var, command=lambda r=row: self.toggle_row(r))
            checkbutton.grid(row=row, column=1, padx=5, pady=5)
            row_widgets.append(enable_var)

            # Spinbox for "Ring Diameter" (0-32, step=1)
            ring_diameter = tk.Spinbox(self, from_=0, to=32, increment=1, width=8, state="disabled", command=self.update_spinbox_value)
            ring_diameter.grid(row=row, column=2, padx=5, pady=5)
            row_widgets.append(ring_diameter)

            # Spinbox for "Circle Diameter" (0-24, step=0.5)
            circle_diameter = tk.Spinbox(self, from_=0, to=24, increment=0.5, width=8, state="disabled", command=self.update_spinbox_value)
            circle_diameter.grid(row=row, column=3, padx=5, pady=5)
            row_widgets.append(circle_diameter)

            # Spinbox for "# Circles" (1-20, step=1)
            num_circles = tk.Spinbox(self, from_=1, to=20, increment=1, width=8, state="disabled", command=self.update_spinbox_value)
            num_circles.grid(row=row, column=4, padx=5, pady=5)
            row_widgets.append(num_circles)

            # Append row widgets to the main widget list
            self.widgets.append(row_widgets)

    def toggle_row(self, row):
        """Enable or disable the widgets in a row based on the state of the Checkbutton."""
        row_widgets = self.widgets[row - 1]  # Get the widgets for the specified row
        is_enabled = row_widgets[0].get()  # Checkbutton state (BooleanVar)

        # Enable or disable the widgets in the row
        state = "normal" if is_enabled else "disabled"
        for widget in row_widgets[1:]:  # Skip the Checkbutton (first element)
            widget.config(state=state)

        self.event_generate("<<UpdateCircleAction>>")  # notify parent

    def update_spinbox_value(self):
        self.event_generate("<<UpdateCircleAction>>")  # notify parent

    def get_ring_data(self):
        """
        Generate pattern data from the current widget values.

        Arguments:
            None

        Returns:
            data (list): A list of circle elements (dicts) defined in mm.
                         example_element = {"type": "circle",
                                            "x": 6.5,
                                            "y": 2.5,
                                            "radius": 1}
        """
        data = []
        for row_widgets in self.widgets:
            ring_enabled = row_widgets[0].get()  # Boolean value from Checkbutton

            if ring_enabled:
                num_circles = int(row_widgets[3].get())  # String value from Spinbox
                ring_radius = float(row_widgets[1].get()) / 2  # String value from Spinbox
                circle_radius = float(row_widgets[2].get()) / 2  # String value from Spinbox
                angles = np.linspace(0, 2 * np.pi, num_circles, endpoint=False)

                for theta in angles:
                    x = ring_radius * np.cos(theta)
                    y = ring_radius * np.sin(theta)
                    data.append({'type': 'circle', 'x': float(x), 'y': float(y), 'radius': float(circle_radius)})

        return data


# Main application demonstrating how to embed the class in an application.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Circle Settings")
    root.resizable(False, False)  # prevent resizing in both width and height

    # Embed CircleSettings class inside the main window
    circle_settings_pane = CircleSettings(root)
    circle_settings_pane.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # use grid to position the pane

    # Configure grid weights for resizing
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Run the application
    root.mainloop()
