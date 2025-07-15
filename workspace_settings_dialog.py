import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser

import entry_validation as ev


class WorkSettingsDialog(tk.Toplevel):
    def __init__(self, parent, workspace_size, workspace_units, background_color, show_origin, origin_position, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.widgets = {}
        self.settings = {}

        self.dialog_title = "Workspace Settings"
        self.content_frame_title = "User Settings"

        self.selected_units = workspace_units
        self.previous_units = self.selected_units
        self.origin_position = origin_position

        # self.origin_position = self.defaults['origin_position']

        # Create a frame for the main widgets.
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=(5, 0))
        self.main_frame.columnconfigure(0, weight=1)

        # Create a frame for the user input widgets.
        self.content_frame = ttk.LabelFrame(self.main_frame, text=f"{self.content_frame_title}")
        self.content_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="ew")

        # Register entry validation functions
        validate_float_pos_cmd = self.register(ev.validate_float_pos)

        # Row 0: Workspace Units
        self.create_input_row(
            self.content_frame,
            row=0,
            key="workspace_units",
            left_label_text="Workspace Units",
            widget_type="radiobutton",
            widget_options={
                "default": workspace_units,
                "options": [("imperial", "in", self.on_units_selected), ("metric", "mm", self.on_units_selected)]  # (value, label, command)
            },
            right_label_text="",
        )

        # Row 1: Workspace Size
        self.create_input_row(
            parent_frame=self.content_frame,
            row=1,
            key="workspace_size",
            left_label_text="Workspace Size",
            widget_type="entry",
            widget_options={
                "default": workspace_size,
                "width": 8,
                "validate": "key",
                "validatecommand": (validate_float_pos_cmd, "%P"),
            },
            right_label_text={"imperial": '[in]', "metric": '[mm]'}[workspace_units]
        )

        # Row 2: Background Color
        self.create_input_row(
            self.content_frame,
            row=2,
            key="background_color",
            left_label_text="Background Color",
            widget_type="colorpicker",
            widget_options={
                "default": background_color
            },
            right_label_text="",
        )

        # Row 3: Show Origin
        self.create_input_row(
            self.content_frame,
            row=3,
            key="show_origin",
            left_label_text="Show Origin",
            widget_type="checkbutton",
            widget_options={
                "default": show_origin
            },
            right_label_text="",
        )

        # Row 4: Origin Position
        self.create_origin_picker(self.content_frame, row=4)

        # Add a cancel button
        self.cancel_button = tk.Button(self.main_frame, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=1, column=0, padx=5, pady=(5, 15), sticky="nse")
        self.bind("<Escape>", self.cancel)

        # Add an apply button
        self.apply_button = tk.Button(self.main_frame, text="Apply", command=self.apply)
        self.apply_button.grid(row=1, column=1, padx=5, pady=(5, 15), sticky="nse")
        self.bind("<Return>", self.apply)

        # Configure window properties.
        self.title(self.dialog_title)
        self.resizable(False, False)
        self.transient(self.parent)  # keep dialog on top of main window
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_idletasks()

        # Position dialog at the center of the parent window.
        if self.parent is not None:
            self.geometry("+%d+%d" % (self.parent.winfo_rootx() + self.parent.winfo_width() / 2.0 - self.winfo_width() / 2.0,
                                      self.parent.winfo_rooty() + self.parent.winfo_height() / 2.0 - self.winfo_height() / 2.0))

        # Make dialog visible and set the widget that has focus.
        self.deiconify()
        self.focus_set()
        self.wait_visibility()

        # Direct all events to this window and its descendents.
        self.grab_set()

        # Stop main script until dialog is dismissed.
        self.wait_window(self)

    def create_layout(self):
        pass

    def create_input_row(self, parent_frame, row, key, left_label_text, widget_type, widget_options=None, right_label_text=None):
        """
        Create a row of GUI elements: a left label, a middle input widget, and an optional right label.

        Args:
            parent_frame (tk.Frame): The parent container to which the row will be added.
            row (int): The row index for grid placement.
            key (str): Dictionary key by which the widgets can be accessed after creation.
            left_label_text (str): Display text for the left label.
            widget_type (str): Type of middle widget ('entry', 'spinbox', 'radiobutton', 'checkbutton', or 'colorpicker').
            widget_options (dict): Options for configuring the middle widget (default: None).
            right_label_text (str): Display text for the optional right label (default: None).

        Returns:
            dict: References to the created widgets (left_label, middle_widget, right_label).
        """
        # Default options for widgets
        widget_options = widget_options or {}

        # Create the left label
        left_label = tk.Label(parent_frame, text=left_label_text, width=16, anchor="w")
        left_label.grid(row=row, column=0, padx=(15, 5), pady=5, sticky="w")

        # Create the middle widget based on the widget type
        if widget_type == "entry":
            var = tk.StringVar(value=widget_options.get("default", ""))
            middle_widget = tk.Entry(
                parent_frame,
                textvariable=var,
                width=widget_options.get("width", 10),
                validate=widget_options.get("validate", "none"),
                validatecommand=widget_options.get("validatecommand"),
            )
            middle_widget.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        elif widget_type == "spinbox":
            var = tk.StringVar(value=widget_options.get("default", ""))
            middle_widget = tk.Spinbox(
                parent_frame,
                from_=widget_options.get("from_", 0),
                to=widget_options.get("to", 100),
                increment=widget_options.get("increment", 1),
                textvariable=var,
                width=widget_options.get("width", 8),
                validate=widget_options.get("validate", "none"),
                validatecommand=widget_options.get("validatecommand"),
            )
            middle_widget.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        elif widget_type == "radiobutton":
            var = tk.StringVar(value=widget_options.get("default", ""))  # default selected value
            middle_widget = tk.Frame(parent_frame)
            for idx, (value, label, command) in enumerate(widget_options.get("options", [])):
                rb = tk.Radiobutton(
                    middle_widget,
                    text=label,
                    value=value,
                    variable=var,
                    command=command
                )
                rb.grid(row=0, column=idx, padx=(0 if idx == 0 else 5, 0), sticky="w")
            middle_widget.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        elif widget_type == "checkbutton":
            var = tk.BooleanVar(value=bool(widget_options.get("default", False)))
            middle_widget = tk.Checkbutton(parent_frame, variable=var, anchor="w")
            middle_widget.grid(row=row, column=1, columnspan=2, padx=(0, 5), pady=5, sticky="w")

        elif widget_type == "colorpicker":
            var = tk.StringVar(value=widget_options.get("default", "pink"))
            middle_widget = tk.Canvas(
                parent_frame,
                width=20,
                height=20,
                bg=var.get(),  # set the initial background color
                highlightthickness=1,  # subtle border thickness
                highlightbackground="dim gray"  # subtle border color
            )

            # Function to open the color chooser and update the Canvas and StringVar
            def pick_color(event=None):
                color_code = colorchooser.askcolor(color=var.get(), title="Choose a color")[1]
                if color_code:  # if a color is selected (not canceled)
                    var.set(color_code)  # update the StringVar with the chosen color
                    middle_widget.config(bg=color_code)  # update the Canvas background color
                    self.event_generate("<<BackgroundColorAction>>")  # notify parent of new color

            middle_widget.bind("<Button-1>", pick_color)
            middle_widget.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        else:
            raise ValueError(f"Unsupported widget type: {widget_type}")

        # Create the optional right label
        right_label = None
        if right_label_text:
            right_label = tk.Label(parent_frame, text=right_label_text, width=6, anchor="w")
            right_label.grid(row=row, column=3, padx=5, pady=5, sticky="w")

        # Store references to widgets for external access
        self.widgets[key] = {"left_label": left_label, "middle_widget": middle_widget, "var": var, "right_label": right_label}

        return self.widgets[key]

    def create_origin_picker(self, parent, row):
        """
        Get the values of all user input widgets for export.
        """
        # Add the label to the left of the buttons
        self.origin_position_label = tk.Label(parent, text="Origin Position")
        self.origin_position_label.grid(row=row, column=0, padx=(15, 5), pady=(5, 10), sticky="w")

        # Create the 3x3 grid of buttons
        self.button_frame = tk.Frame(parent)
        self.button_frame.grid(row=row, column=1, padx=0, pady=(5, 15), sticky="w")

        # Dictionary to store button references
        self.buttons = {}

        # Create a 3x3 grid of buttons
        arrows = ["↖", "↑", "↗", "←", "•", "→", "↙", "↓", "↘"]
        for i in range(3):
            for j in range(3):
                button = tk.Button(
                    self.button_frame,
                    text=arrows[i * 3 + j],
                    font=("Arial", 10),
                    width=2,
                    height=1,
                    relief="sunken" if (i, j) == self.origin_position else "raised",  # preselect button
                    command=lambda b=(i, j): self.toggle_button(b)  # pass button position
                )
                button.grid(row=i, column=j, padx=2, pady=2)
                self.buttons[(i, j)] = button  # store a reference to the button

    def on_units_selected(self):
        """
        Callback method called when unit radio button is selected.
        """
        units = self.get_widget_value('workspace_units')
        units_changed = True if units != self.previous_units else False

        # Update righthand label for workspace size field.
        label = {'imperial': '[in]', 'metric': '[mm]'}
        self.widgets['workspace_size']['right_label'].config(text=label[units])

        # Convert field value if unit system changed.
        if units_changed:
            workspace_width_entry = self.get_widget_value('workspace_size')
            if workspace_width_entry:
                workspace_width = self.convert_value(float(workspace_width_entry), units)
                workspace_width_rounded = round(workspace_width, 5)
                self.set_widget_value('workspace_size', workspace_width_rounded)
                self.widgets['workspace_size']['middle_widget'].icursor(tk.END)  # move cursor to end of line

        self.previous_units = units

    def convert_value(self, value, units):
        """
        Converts a value to the specified unit system.

        Args:
            value (float): The value in the current unit system.
            units (str): The target unit system, either "metric" or "imperial".

        Returns:
            float: The converted value in the target unit system.
        """
        if units == "metric":
            return (25.4 * value)
        elif units == "imperial":
            return (value / 25.4)
        else:
            raise ValueError("Invalid unit system. Use 'metric' or 'imperial'.")

    def toggle_button(self, button_id):
        """
        Toggle the visual state of the button.
        Ensure only one button can be in the sunken (depressed) state.
        """
        # If a button is already selected, reset it to normal
        if self.origin_position is not None:
            prev_button = self.buttons[self.origin_position]
            prev_button.config(relief="raised")

        # Set the new button to sunken state
        new_button = self.buttons[button_id]
        new_button.config(relief="sunken")

        # Update the currently selected button
        self.origin_position = button_id

    def get_widget_value(self, key):
        """
        Get the value of a widget based on its key.

        Args:
            key (str): The text of the key.

        Returns:
            Any: The current value of the associated widget.
        """
        widget_info = self.widgets.get(key)
        if not widget_info:
            return None

        var = widget_info["var"]
        if isinstance(var, (tk.StringVar, tk.BooleanVar)):
            return var.get()
        else:
            return None

    def set_widget_value(self, key, value):
        """
        Set the value of a widget based on its key.

        Args:
            key (str): The text of the key.
            value (any): The value to set for the associated widget.
        """
        widget_info = self.widgets.get(key)
        if not widget_info:
            return

        var = widget_info["var"]
        if isinstance(var, (tk.StringVar, tk.BooleanVar)):
            var.set(value)

    def close(self, event=None):
        """Return focus to the parent window and close."""
        if self.parent is not None:
            self.parent.focus_set()
        tk.Toplevel.destroy(self)

    def apply(self, event=None):
        """Gather dialog settings and close window."""
        self.settings = {}
        for key in self.widgets.keys():
            self.settings[key] = self.get_widget_value(key)
        self.settings['origin_position'] = self.origin_position
        self.close()

    def cancel(self, event=None):
        """Clear dialog settings and close."""
        self.settings = {}
        self.close()

    def get_settings(self):
        """Return the current state of the dialog widgets."""
        return self.settings


class DemoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Window")
        self.geometry("300x200")
        self.resizable(False, False)  # prevent resizing in both width and height

        # Button to open the pop-up dialog
        open_dialog_button = tk.Button(self, text="Open Dialog", command=self.open_dialog)
        open_dialog_button.pack(pady=50)

    def open_dialog(self):
        # Raise an example instance of the dialog.
        d = WorkSettingsDialog(parent=self,
                               workspace_size=1.25,
                               workspace_units='imperial',
                               background_color='#FFFF80',
                               show_origin=True,
                               origin_position=(1, 1))

        print(d.get_settings())


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
