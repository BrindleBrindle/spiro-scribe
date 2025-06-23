import os
import tkinter as tk
import entry_validation as ev

from tkinter import ttk
from tkinter import colorchooser
from tkinter import filedialog
from PIL import Image, ImageTk


class ExportSVGDialog(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        """
        Dialog to generate SVG file.

        Args:
            parent (tk.Tk): Parent tkinter application window.
        """
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.widgets = {}  # store references to widgets for easy access
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
                         "stroke_width": 0.25,
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
        validate_int_pos_cmd = self.register(ev.validate_int_pos)
        validate_float_pos_cmd = self.register(ev.validate_float_pos)
        validate_resolution_cmd = self.register(ev.validate_resolution)

        self.create_row(
            self.svg_lf,
            row=0,
            left_label_text="Image Width",
            widget_type="entry",
            widget_options={
                "default": self.defaults['svg_width'],
                "width": 16,
                "validate": "key",
                "validatecommand": (validate_int_pos_cmd, "%P"),
            },
            right_label_text="[px]",
        )

        self.create_row(
            self.svg_lf,
            row=1,
            left_label_text="Image Height",
            widget_type="entry",
            widget_options={
                "default": self.defaults['svg_height'],
                "width": 16,
                "validate": "key",
                "validatecommand": (validate_int_pos_cmd, "%P"),
            },
            right_label_text="[px]",
        )

        self.create_row(
            self.svg_lf,
            row=2,
            left_label_text="Stroke Width",
            widget_type="entry",
            widget_options={
                "default": self.defaults['stroke_width'],
                "width": 16,
                "validate": "key",
                "validatecommand": (validate_float_pos_cmd, "%P"),
            },
            right_label_text="[dwg units]",
        )

        self.create_row(
            self.svg_lf,
            row=3,
            left_label_text="Path Resolution",
            widget_type="spinbox",
            widget_options={
                "default": self.defaults['path_resolution'],
                "from_": 16,
                "to": 5000,
                "increment": 10,
                "validate": "key",
                "validatecommand": (validate_resolution_cmd, "%P"),
            },
            right_label_text="[divs/360°]",
        )

        self.create_row(
            self.svg_lf,
            row=4,
            left_label_text="Background Color",
            widget_type="colorpicker",
            widget_options={
                "default": self.defaults['background_color'],
            },
            right_label_text="",
        )

        self.create_row(
            self.svg_lf,
            row=5,
            left_label_text="Stroke Color",
            widget_type="colorpicker",
            widget_options={
                "default": self.defaults['stroke_color'],
            },
            right_label_text="",
        )

        self.create_row(
            self.svg_lf,
            row=6,
            left_label_text="Include Parameters",
            widget_type="checkbutton",
            widget_options={"default": True},
        )

        cwd = os.getcwd()
        folder_image = Image.open(cwd + "\\images\\" + "folder.png")
        resized_folder_image = folder_image.resize((18, 18))  # resize to fit the button
        folder_button_image = ImageTk.PhotoImage(resized_folder_image)

        self.out_location_label = tk.Label(self.main_frame, anchor="w", text="Output")
        self.out_location_var = tk.StringVar(value="")
        self.out_location_entry = tk.Entry(self.main_frame, state="disabled", textvariable=self.out_location_var)
        self.out_location_button = tk.Button(self.main_frame, anchor="w", image=folder_button_image,
                                             command=self.raise_save_as_dialog)
        self.out_location_label.grid(row=2, column=0, padx=(10, 5), pady=(5, 10), sticky="w")
        self.out_location_entry.grid(row=2, column=1, padx=(5, 5), pady=(5, 10), sticky="nsew")
        self.out_location_button.grid(row=2, column=2, padx=(5, 10), pady=(5, 10), sticky="w")
        self.out_location_button.image = folder_button_image  # keep a reference

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

    def create_row(self, parent_frame, row, left_label_text, widget_type, widget_options=None, right_label_text=None):
        """
        Create a row of GUI elements: a left label, a middle input widget, and an optional right label.

        Args:
            parent_frame (tk.Frame): The parent container to which the row will be added.
            row (int): The row index for grid placement.
            left_label_text (str): Text for the left label.
            widget_type (str): Type of middle widget ('entry', 'spinbox', 'checkbutton', or 'colorpicker').
            widget_options (dict): Options for configuring the middle widget (default: None).
            right_label_text (str): Text for the optional right label (default: None).

        Returns:
            dict: References to the created widgets (left_label, middle_widget, right_label).
        """
        # Default options for widgets
        widget_options = widget_options or {}

        # Create the left label
        left_label = tk.Label(parent_frame, text=left_label_text, width=16, anchor="e")
        left_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")

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
            right_label = tk.Label(parent_frame, text=right_label_text, width=16, anchor="w")
            right_label.grid(row=row, column=3, padx=5, pady=5, sticky="w")

        # Store references to widgets for external access
        self.widgets[left_label_text] = {"left_label": left_label, "middle_widget": middle_widget, "var": var, "right_label": right_label}

        return self.widgets[left_label_text]

    def get_widget_value(self, label_text):
        """
        Get the value of a widget based on the left label's text.

        Args:
            label_text (str): The text of the left label.

        Returns:
            Any: The current value of the associated widget.
        """
        widget_info = self.widgets.get(label_text)
        if not widget_info:
            return None

        var = widget_info["var"]
        if isinstance(var, (tk.StringVar, tk.BooleanVar)):
            return var.get()
        else:
            return None

    def set_widget_value(self, label_text, value):
        """
        Set the value of a widget based on the left label's text.

        Args:
            label_text (str): The text of the left label.
            value (any): The value to set for the associated widget.
        """
        widget_info = self.widgets.get(label_text)
        if not widget_info:
            return

        var = widget_info["var"]
        if isinstance(var, (tk.StringVar, tk.BooleanVar)):
            var.set(value)

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
        svg_parameters['svg_width'] = int(self.get_widget_value("Image Width"))
        svg_parameters['svg_height'] = int(self.get_widget_value("Image Height"))
        svg_parameters['stroke_width'] = float(self.get_widget_value("Stroke Width"))
        svg_parameters['path_resolution'] = int(self.get_widget_value("Path Resolution"))
        svg_parameters['background_color'] = self.get_widget_value("Background Color")
        svg_parameters['stroke_color'] = self.get_widget_value("Stroke Color")
        svg_parameters['include_params'] = bool(self.get_widget_value("Include Parameters"))

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
