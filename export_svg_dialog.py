import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from tkinter import colorchooser  # for the color picker
from tkinter import filedialog


class ExportSVGDialog(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        """
        Dialog to generate SVG file.

        Args:
            parent (tk.Tk): Parent tkinter application window.
        """
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("Export to SVG")
        self.resizable(False, False)
        self.transient(parent)  # keep dialog on top of main window

        # Set window to delete itself when the cancel button is pressed.
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_idletasks()

        # Position dialog at the center of the parent window.
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() / 2.0 - self.winfo_width() / 2.0,
                                      parent.winfo_rooty() + parent.winfo_height() / 2.0 - self.winfo_height() / 2.0))

        self.defaults = {"svg_width": 400,
                         "svg_height": 400,
                         "background_color": "whitesmoke",
                         "stroke_color": "slategray",
                         "stroke_width": 0.5,
                         "include_params": True,
                         "path_resolution": 1000}

        self.settings = {}
        self.file_path = None

        # Create a frame for the main widgets
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=(5, 0))
        self.main_frame.columnconfigure(1, weight=1)

        self.svg_lf = ttk.LabelFrame(self.main_frame, text="SVG Parameters")
        self.svg_lf.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        self.svg_lf.columnconfigure(0, weight=0)
        self.svg_lf.columnconfigure(2, weight=1)

        # Register entry validation functions
        validate_intpos_cmd = self.register(self.validate_intpos)
        validate_floatpos_cmd = self.register(self.validate_floatpos)
        validate_resolution_cmd = self.register(self.validate_resolution)

        self.width_label_1 = tk.Label(self.svg_lf, anchor="e", width=16, text="Image Width")
        self.width_var = tk.StringVar(value=self.defaults['svg_width'])
        self.width_entry = tk.Entry(self.svg_lf, textvariable=self.width_var,
                                    validate="key", validatecommand=(validate_intpos_cmd, "%P"), width=15)
        self.width_label_2 = tk.Label(self.svg_lf, width=16, anchor="w", text="[px]")
        self.width_label_1.grid(row=1, column=0, padx=5, pady=(10, 5), sticky="w")
        self.width_entry.grid(row=1, column=1, columnspan=2, pady=(10, 5), sticky="ew")
        self.width_label_2.grid(row=1, column=3, padx=5, pady=(10, 5), sticky="ew")

        self.height_label_1 = tk.Label(self.svg_lf, anchor="e", width=16, text="Image Height")
        self.height_var = tk.StringVar(value=self.defaults['svg_height'])
        self.height_entry = tk.Entry(self.svg_lf, textvariable=self.height_var,
                                     validate="key", validatecommand=(validate_intpos_cmd, "%P"), width=15)
        self.height_label_2 = tk.Label(self.svg_lf, width=16, anchor="w", text="[px]")
        self.height_label_1.grid(row=2, column=0, padx=5, pady=5, stick="w")
        self.height_entry.grid(row=2, column=1, columnspan=2, sticky="ew")
        self.height_label_2.grid(row=2, column=3, padx=5, sticky="ew")

        self.stroke_width_label_1 = tk.Label(self.svg_lf, anchor="e", width=16, text="Stroke Width")
        self.stroke_width_var = tk.StringVar(value=self.defaults['stroke_width'])
        self.stroke_width_entry = tk.Entry(self.svg_lf, textvariable=self.stroke_width_var,
                                           validate="key", validatecommand=(validate_floatpos_cmd, "%P"), width=15)
        self.stroke_width_label_2 = tk.Label(self.svg_lf, width=16, anchor="w", text="[mm]")
        self.stroke_width_label_1.grid(row=3, column=0, padx=5, pady=5, stick="w")
        self.stroke_width_entry.grid(row=3, column=1, columnspan=2, sticky="ew")
        self.stroke_width_label_2.grid(row=3, column=3, padx=5, sticky="ew")

        self.res_label_1 = tk.Label(self.svg_lf, width=16, anchor="e", text="Path Resolution")
        self.res_var = tk.StringVar(value=self.defaults['path_resolution'])
        self.res_spinbox = tk.Spinbox(self.svg_lf, from_=100, to=5000, increment=10, width=8,
                                      validate="key", validatecommand=((validate_resolution_cmd, "%P")),
                                      textvariable=self.res_var)
        self.res_label_2 = tk.Label(self.svg_lf, width=16, anchor="w", text="[divs/360\u00B0]")
        self.res_label_1.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.res_spinbox.grid(row=4, column=1, columnspan=2, pady=5, sticky="ew")
        self.res_label_2.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        self.create_color_picker(self.svg_lf, row=5, label_text="Background Color", default_color=self.defaults['background_color'])
        self.create_color_picker(self.svg_lf, row=6, label_text="Stroke Color", default_color=self.defaults['stroke_color'])

        self.include_params_label = tk.Label(self.svg_lf, width=16, anchor="e", text="Include Parameters")
        self.include_params_var = tk.BooleanVar(value=self.defaults['include_params'])
        self.include_params_checkbutton = tk.Checkbutton(self.svg_lf, variable=self.include_params_var)
        self.include_params_label.grid(row=7, column=0, padx=(5, 0), pady=(5, 10), sticky="w")
        self.include_params_checkbutton.grid(row=7, column=1, sticky="ew")

        cwd = os.getcwd()
        folder_image = Image.open(cwd + "\\images\\" + "folder.png")
        resized_folder_image = folder_image.resize((18, 18))  # Resize to fit the button
        folder_button_image = ImageTk.PhotoImage(resized_folder_image)

        self.out_location_label = tk.Label(self.main_frame, anchor="w", text="Output")
        self.out_location_var = tk.StringVar(value="")
        self.out_location_entry = tk.Entry(self.main_frame, state="disabled", textvariable=self.out_location_var)
        self.out_location_button = tk.Button(self.main_frame, anchor="w", image=folder_button_image,
                                             command=self.raise_save_as_dialog)
        self.out_location_label.grid(row=2, column=0, padx=(10, 5), pady=(5, 10), sticky="w")
        self.out_location_entry.grid(row=2, column=1, padx=(5, 5), pady=(5, 10), sticky="nsew")
        self.out_location_button.grid(row=2, column=2, padx=(5, 10), pady=(5, 10), sticky="w")
        self.out_location_button.image = folder_button_image  # Keep a reference

        self.export_button_frame = tk.Frame(self)
        self.export_button_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.export_button_frame.columnconfigure(0, weight=1)

        # Add a cancel button
        self.cancel_button = tk.Button(self.export_button_frame, text="Cancel", command=self.close)
        self.cancel_button.grid(row=0, column=0, padx=5, pady=(5, 5), sticky="nse")
        self.bind("<Return>", self.close)

        # Add an export button
        self.export_button = tk.Button(self.export_button_frame, state="disabled", text="Export", command=self.export)
        self.export_button.grid(row=0, column=1, padx=5, pady=(5, 5), sticky="nse")
        self.bind("<Return>", self.close)

        # Make dialog visible and set the widget that has focus.
        self.deiconify()
        self.focus_set()
        self.wait_visibility()

        # Direct all events to this window and its descendents.
        self.grab_set()

        # Stop main script until dialog is dismissed.
        self.wait_window(self)

    def create_color_picker(self, parent, row, label_text, default_color):
        """Helper function to create a Label and a color picker square in a row."""
        label = tk.Label(parent, text=label_text, width=16, anchor="e")
        label.grid(row=row, column=0, padx=5, pady=5)

        # Create a small square to display the selected color with a subtle border
        self.color_display = tk.Canvas(
            parent,
            width=20,
            height=20,
            bg=default_color,  # set to the initial default color
            highlightthickness=1,  # subtle border thickness
            highlightbackground="dim gray"  # subtle border color
        )
        self.color_display.grid(row=row, column=1, padx=0, pady=5, sticky="w")

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

    def convert_value(self, value, units):
        """
        Convert a value to the specified unit system.

        Arguments:
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

    def validate_intpos(self, new_value):
        """
        Validates the input to ensure it is an integer greater than zero.

        Args:
            new_value (str): The current value of the Entry widget after the change.

        Returns:
            bool: True if the input is a valid int or empty, False otherwise.
        """
        if new_value == "":  # Allow empty string (to enable deletion)
            return True
        try:
            return True if int(new_value) > 0 else False
        except ValueError:
            return False  # Reject input if it's not a valid int

    def validate_floatpos(self, new_value):
        """
        Validates the input to ensure it is a float greater than zero.

        Arguments:
            new_value (str): The current value of the Entry widget after the change.

        Returns:
            bool: True if the input is a valid float or empty, False otherwise.
        """
        if new_value == "":  # Allow empty string (to enable deletion)
            return True
        try:
            return True if float(new_value) > 0 else False
        except ValueError:
            return False  # Reject input if it's not a valid float

    def validate_resolution(self, new_value):
        """
        Validates the input to ensure it is a valid arc resolution value.

        Args:
            new_value (str): The current value of the Spinbox widget after the change.

        Returns:
            bool: True if the input is a valid resolution or empty, False otherwise.
        """
        if new_value == "":  # Allow empty string (to enable deletion)
            return True
        try:
            return True if (int(new_value) > 0) and (int(new_value) <= 5000) else False
        except ValueError:
            return False  # Reject input if it's not a valid int

    def raise_save_as_dialog(self):
        file_path = filedialog.asksaveasfilename(title="Select Output Location",
                                                 defaultextension=".svg", 
                                                 filetypes=[("SVG File", "*.svg")],
                                                 initialdir=os.getcwd())

        if file_path:
            self.export_button.configure(state='normal')
            self.out_location_var.set(file_path)
            self.file_path = file_path

    def export(self, event=None):
        svg_parameters = {}
        # TODO: Collect up all SVG parameters.

        self.settings = {"file_path": self.file_path,
                         "svg_parameters": svg_parameters}

        self.close()

    def cancel(self, event=None):
        """Clear dialog settings and close."""
        self.settings = {}
        self.close()

    def close(self, event=None):
        """Return focus to the parent window and close."""
        if self.parent is not None:
            self.parent.focus_set()
        tk.Toplevel.destroy(self)

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
        # Raise an instance of the dialog.
        ExportSVGDialog(self)


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
