import tkinter as tk
from tkinter import ttk


class RouletteSettings(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Column and row headings
        # column_headings = ["Enable", "Radius A", "Radius B", "Roll Side", "Pen Distance", "Resolution"]
        column_headings = ["Enable", "Radius A", "Radius B", "Roll Side", "Pen Distance"]

        # Create table headers
        for col, heading in enumerate(column_headings):  # the first column is for row headings
            label = tk.Label(self, text=heading)
            label.grid(row=0, column=col, padx=5, pady=5)

        # Create the table rows
        self.widgets = []  # store widget references for later use

        # Checkbutton for Enable
        enable_var = tk.BooleanVar(value=False)
        enable_checkbutton = tk.Checkbutton(self, variable=enable_var, command=self.toggle_widgets)
        enable_checkbutton.grid(row=1, column=0, padx=5, pady=5)
        self.widgets.append(enable_var)

        # Spinbox for Radius A (Static Circle)
        radius_A_value = tk.StringVar(value=5)
        radius_A_spinbox = tk.Spinbox(self, from_=0, to=32, increment=0.5, width=8, state="disabled", command=self.update_parameter_value, textvariable=radius_A_value)
        radius_A_spinbox.grid(row=1, column=1, padx=5, pady=5)
        self.widgets.append(radius_A_spinbox)

        # Spinbox for Radius B (Rolling Circle)
        radius_B_value = tk.StringVar(value=2)
        radius_B_spinbox = tk.Spinbox(self, from_=0.5, to=24, increment=0.5, width=8, state="disabled", command=self.update_parameter_value, textvariable=radius_B_value)
        radius_B_spinbox.grid(row=1, column=2, padx=5, pady=5)
        self.widgets.append(radius_B_spinbox)

        # Spinbox for Roll Side
        roll_side_combobox = ttk.Combobox(self, values=["Inside", "Outside"], state="disabled", width=8)
        roll_side_combobox.set("Inside")  # set default value
        roll_side_combobox.state(["readonly"])
        roll_side_combobox.bind("<<ComboboxSelected>>", self.update_parameter_value)
        roll_side_combobox.grid(row=1, column=3, padx=5, pady=5)
        self.widgets.append(roll_side_combobox)

        # Spinbox for Pen Distance
        pen_distance_value = tk.StringVar(value=2)
        pen_distance_spinbox = tk.Spinbox(self, from_=0, to=10, increment=0.5, width=8, state="disabled", command=self.update_parameter_value, textvariable=pen_distance_value)
        pen_distance_spinbox.grid(row=1, column=4, padx=5, pady=5)
        self.widgets.append(pen_distance_spinbox)

    def toggle_widgets(self):
        """Enable or disable the widgets based on the state of the Checkbutton."""
        is_enabled = self.widgets[0].get()  # checkbutton state (BooleanVar)

        # Enable or disable the widgets
        for widget in self.widgets[1:]:  # skip the Checkbutton (first element)
            if isinstance(widget, tk.Spinbox) or isinstance(widget, tk.Scale):  # handle Spinbox
                state = "normal" if is_enabled else "disabled"
                widget.config(state=state)
            elif isinstance(widget, ttk.Combobox):  # handle Combobox
                state = "readonly" if is_enabled else "disabled"
                widget.config(state=state)

        self.event_generate("<<UpdateRouletteAction>>")  # notify parent

    def update_parameter_value(self, event=None):
        self.event_generate("<<UpdateRouletteAction>>")  # notify parent

    def get_roulette_data(self):
        """
        Generate pattern data for the widgets.

        Arguments:
            None

        Returns:
            data (dict): Dictionary containing the selected roulette parameters.
        """
        data = {}
        enabled = self.widgets[0].get()  # Boolean value from Checkbutton

        if enabled:
            data['type'] = "roulette"
            data['R'] = float(self.widgets[1].get())
            data['r'] = float(self.widgets[2].get())
            data['s'] = {"Inside": -1, "Outside": 1}.get(self.widgets[3].get())  # translate string from combo to number
            data['d'] = float(self.widgets[4].get())
            data['display res'] = 200

        return data


# Main application demonstrating how to embed the class in an application.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Roulette Settings")
    root.resizable(False, False)  # prevent resizing in both width and height

    # Embed RouletteSettings class inside the main window
    roulette_settings_pane = RouletteSettings(root)
    roulette_settings_pane.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # use grid to position the pane

    # Configure grid weights for resizing
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Run the application
    root.mainloop()
