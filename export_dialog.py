import os
import tkinter as tk
import entry_validation as ev

from tkinter import ttk
from tkinter import colorchooser
from tkinter import filedialog
from PIL import Image, ImageTk


class ExportDialog(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        """
        Generic file export dialog.

        Args:
            parent (tk.Tk): Parent tkinter application window.
        """
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.widgets = {}
        self.settings = {}
        self.file_path = None

        # Initialize dialog settings.
        self.initialize_dialog_settings()

        # Create dialog layout.
        self.create_layout()

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

    def initialize_dialog_settings(self):
        """
        Hook for subclasses to customize dialog settings.
        """
        self.dialog_title = "Export Dialog"
        self.content_frame_title = "User Settings"
        self.defaultextension = None
        self.filetypes = [("All Files", "*.*")]

        self.defaults = {
            "entry": 10,
            "spinbox": 10,
            "radiobutton": "1",
            "checkbutton": True,
            "colorpicker": "lavender"
        }

    def create_layout(self):
        # Create a frame for the main widgets.
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=(5, 0))
        self.main_frame.columnconfigure(1, weight=1)

        # Create a frame for the user input widgets.
        self.content_frame = ttk.LabelFrame(self.main_frame, text=f"{self.content_frame_title}")
        self.content_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=(5, 10), sticky="ew")
        self.content_frame.columnconfigure(0, weight=0)
        self.content_frame.columnconfigure(2, weight=1)

        # Create output path bar.
        cwd = os.getcwd()
        folder_image = Image.open(cwd + "\\images\\" + "folder.png")
        resized_folder_image = folder_image.resize((18, 18))  # resize to fit the button
        folder_button_image = ImageTk.PhotoImage(resized_folder_image)

        self.out_location_label = tk.Label(self.main_frame, anchor="w", text="Output")
        self.out_location_var = tk.StringVar(value="")
        self.out_location_entry = tk.Entry(self.main_frame, state="disabled", textvariable=self.out_location_var)
        self.out_location_button = tk.Button(self.main_frame, anchor="w", image=folder_button_image,
                                             command=self.raise_save_as)
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

        # Allow subclasses to add content.
        self.add_content()

    def add_content(self):
        """
        Hook for subclasses to add custom widgets to the content frame.
        """

        # Add an empty row for padding
        spacer = tk.Frame(self.content_frame)
        spacer.grid(row=0, column=0, columnspan=4, pady=3)  # add extra vertical padding

        # Register entry validation functions
        validate_int_pos_cmd = self.register(ev.validate_int_pos)

        self.create_input_row(
            self.content_frame,
            row=1,
            left_label_text="Sample Entry",
            widget_type="entry",
            widget_options={
                "default": self.defaults['entry'],
                "width": 16,
                "validate": "key",
                "validatecommand": (validate_int_pos_cmd, "%P"),
            },
            right_label_text="[units]",
        )

        self.create_input_row(
            self.content_frame,
            row=2,
            left_label_text="Sample Spinbox",
            widget_type="spinbox",
            widget_options={
                "default": self.defaults['spinbox'],
                "from_": 1,
                "to": 100,
                "increment": 1,
                "width": 8,
                "validate": "key",
                "validatecommand": (validate_int_pos_cmd, "%P"),
            },
            right_label_text="[units]",
        )

        self.create_input_row(
            self.content_frame,
            row=3,
            left_label_text="Sample Radiobutton",
            widget_type="radiobutton",
            widget_options={
                "default": self.defaults['radiobutton'],
                "options": [("1", "Option 1", None), ("2", "Option 2", None)],  # (value, label, command)
            },
            right_label_text="",
        )

        self.create_input_row(
            self.content_frame,
            row=4,
            left_label_text="Sample Checkbutton",
            widget_type="checkbutton",
            widget_options={
                "default": self.defaults['checkbutton']
            },
            right_label_text="",
        )

        self.create_input_row(
            self.content_frame,
            row=5,
            left_label_text="Sample Colorpicker",
            widget_type="colorpicker",
            widget_options={
                "default": self.defaults['colorpicker']
            },
            right_label_text="",
        )

        # Add an empty row for padding
        spacer = tk.Frame(self.content_frame)
        spacer.grid(row=6, column=0, columnspan=4, pady=3)  # add extra vertical padding

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
            right_label = tk.Label(parent_frame, text=right_label_text, width=16, anchor="w")
            right_label.grid(row=row, column=3, padx=5, pady=5, sticky="w")

        # Store references to widgets for external access
        self.widgets[key] = {"left_label": left_label, "middle_widget": middle_widget, "var": var, "right_label": right_label}

        return self.widgets[key]

    def get_widget_values(self):
        """
        Get the values of all user input widgets for export.
        """
        widget_values = {}
        for key in self.widgets.keys():
            widget_values[key] = self.get_widget_value(key)

        return widget_values

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

    def raise_save_as(self):
        file_path = filedialog.asksaveasfilename(title="Select Output Location",
                                                 defaultextension=self.defaultextension, 
                                                 filetypes=self.filetypes,
                                                 initialdir=os.getcwd())

        if file_path:
            self.export_button.configure(state='normal')
            self.out_location_var.set(file_path)
            self.file_path = file_path

    def export(self, event=None):
        """Gather dialog settings and close window. Overload in subclass if necessary."""
        self.settings = {"file_path": self.file_path} | self.get_widget_values()  # concatenate dicts
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
        ExportDialog(self)


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
