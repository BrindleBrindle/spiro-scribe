import tkinter as tk
import entry_validation as ev

from export_dialog import ExportDialog


class ExportSVGDialog(ExportDialog):
    def __init__(self, parent, *args, **kwargs):
        """
        Dialog to generate SVG file.

        Args:
            parent (tk.Tk): Parent tkinter application window.
        """
        super().__init__(parent, *args, **kwargs)

    def initialize_dialog_settings(self):
        """
        Hook for subclasses to customize dialog settings.
        """
        self.dialog_title = "Export to SVG"
        self.content_frame_title = "SVG Parameters"
        self.defaultextension = ".svg"
        self.filetypes = [("SVG File", "*.svg")]

        self.defaults = {"svg_width": 400,
                         "svg_height": 400,
                         "background_color": "whitesmoke",
                         "stroke_color": "slategray",
                         "stroke_width": 0.25,
                         "include_params": True,
                         "path_resolution": 1000}

    def add_content(self):
        """
        Hook for subclasses to add custom widgets to the content frame.
        """
        # Register entry validation functions
        validate_int_pos_cmd = self.register(ev.validate_int_pos)
        validate_float_pos_cmd = self.register(ev.validate_float_pos)
        validate_resolution_cmd = self.register(ev.validate_resolution)

        self.create_input_row(
            self.content_frame,
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

        self.create_input_row(
            self.content_frame,
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

        self.create_input_row(
            self.content_frame,
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

        self.create_input_row(
            self.content_frame,
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

        self.create_input_row(
            self.content_frame,
            row=4,
            left_label_text="Background Color",
            widget_type="colorpicker",
            widget_options={
                "default": self.defaults['background_color'],
            },
            right_label_text="",
        )

        self.create_input_row(
            self.content_frame,
            row=5,
            left_label_text="Stroke Color",
            widget_type="colorpicker",
            widget_options={
                "default": self.defaults['stroke_color'],
            },
            right_label_text="",
        )

        self.create_input_row(
            self.content_frame,
            row=6,
            left_label_text="Include Parameters",
            widget_type="checkbutton",
            widget_options={"default": True},
        )


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
        d = ExportSVGDialog(self)
        print(d.get_settings())


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
