import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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

        # TODO: Add self.default_settings here.

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
        # TODO: Add validation functions here
        validate_float_cmd = self.register(self.validate_float)

        self.example_label_1 = tk.Label(self.svg_lf, anchor="w", text="Parameter 1")
        self.example_var = tk.StringVar()
        self.example_entry = tk.Entry(self.svg_lf, textvariable=self.example_var,
                                      validate="key", validatecommand=(validate_float_cmd, "%P"), width=15)
        self.example_label_2 = tk.Label(self.svg_lf, width=16, anchor="w", text="[units]")
        self.example_label_1.grid(row=1, column=0, padx=5, pady=5)
        self.example_entry.grid(row=1, column=1, columnspan=2, sticky="ew")
        self.example_label_2.grid(row=1, column=3, padx=5, sticky="ew")

        self.example_label_3 = tk.Label(self.svg_lf, anchor="w", text="Parameter 2")
        self.example_var = tk.StringVar()
        self.example_entry = tk.Entry(self.svg_lf, textvariable=self.example_var,
                                      validate="key", validatecommand=(validate_float_cmd, "%P"), width=15)
        self.example_label_4 = tk.Label(self.svg_lf, width=16, anchor="w", text="[units]")
        self.example_label_3.grid(row=2, column=0, padx=5, pady=5)
        self.example_entry.grid(row=2, column=1, columnspan=2, sticky="ew")
        self.example_label_4.grid(row=2, column=3, padx=5, sticky="ew")

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

    def convert_value(self, value, units):
        """
        Convert a value to the specified unit system.

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

    def validate_float(self, new_value):
        """
        Validates the input to ensure it is a valid float number.

        Args:
            new_value (str): The current value of the Entry widget after the change.

        Returns:
            bool: True if the input is a valid float, a dash as the first character,
                  or empty, False otherwise.
        """
        if new_value == "":  # Allow empty string (to enable deletion)
            return True
        if new_value == "-":  # Allow a single dash as the first character
            return True
        try:
            float(new_value)  # Try to convert to float
            return True
        except ValueError:
            return False  # Reject input if it's not a valid float

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
