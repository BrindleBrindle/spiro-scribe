import os
import tkinter as tk
import standard_sequences as sseq
import entry_validation as ev

from tkinter import ttk
from PIL import Image, ImageTk
from edit_sequence_dialog import EditSequenceDialog
from export_dialog import ExportDialog


class ExportGCodeDialog(ExportDialog):
    def __init__(self, parent, units, *args, **kwargs):
        """
        Dialog to generate G Code toolpaths.

        Args:
            parent (tk.Tk): Parent tkinter application window.
        """
        self.selected_units = units
        super().__init__(parent, *args, **kwargs)

    def initialize_dialog_settings(self):
        """
        Hook for subclasses to customize dialog settings.
        """
        self.dialog_title = "Export to G Code"
        self.content_frame_title = "Toolpaths Parameters"
        self.defaultextension = ".nc"
        self.filetypes = [("G-Code File", "*.nc")]

        if self.selected_units == 'imperial':
            self.defaults = {"safe_z": "0.25",
                             "jog_feed_xyz": "8.0",
                             "cut_feed_xy": "2.0",
                             "cut_feed_z": "1.0",
                             "depth_per_pass": "0.02",
                             "num_passes": 1,
                             "cut_res": 200
                             }
            self.unit_labels = {"length": "in",
                                "speed": "in/min"
                                }
        else:
            self.defaults = {"safe_z": "6.35",
                             "jog_feed_xyz": "200",
                             "cut_feed_xy": "50",
                             "cut_feed_z": "25",
                             "depth_per_pass": "0.5",
                             "num_passes": 1,
                             "cut_res": 200
                             }
            self.unit_labels = {"length": "mm",
                                "speed": "mm/min"
                                }

        # Set starting sequences to default
        self.sequences = {}
        self.sequences['title'] = sseq.get_sequence("title", units=self.selected_units)
        self.sequences['start'] = sseq.get_sequence("start", units=self.selected_units)
        self.sequences['end'] = sseq.get_sequence("end")

    def add_content(self):
        """
        Hook for subclasses to add custom widgets to the content frame.
        """
        # Add an empty row for padding
        spacer = tk.Frame(self.content_frame)
        spacer.grid(row=0, column=0, columnspan=4, pady=3)  # add extra vertical padding

        # Register the validation function
        validate_float_cmd = self.register(ev.validate_float)
        validate_float_pos_cmd = self.register(ev.validate_float_pos)
        validate_resolution_cmd = self.register(ev.validate_resolution)
        validate_passes_cmd = self.register(ev.validate_passes)

        self.create_input_row(
            self.content_frame,
            row=1,
            left_label_text="Safe Z Height",
            widget_type="entry",
            widget_options={
                "default": self.defaults['safe_z'],
                "width": 16,
                "validate": "key",
                "validatecommand": (validate_float_cmd, "%P"),
            },
            right_label_text=f"[{self.unit_labels['length']}]",
        )

        self.create_input_row(
            self.content_frame,
            row=2,
            left_label_text="Jog feedrate (XYZ)",
            widget_type="entry",
            widget_options={
                "default": self.defaults['jog_feed_xyz'],
                "width": 16,
                "validate": "key",
                "validatecommand": (validate_float_pos_cmd, "%P"),
            },
            right_label_text=f"[{self.unit_labels['speed']}]",
        )

        self.create_input_row(
            self.content_frame,
            row=3,
            left_label_text="Cut feedrate (XY)",
            widget_type="entry",
            widget_options={
                "default": self.defaults['cut_feed_xy'],
                "width": 16,
                "validate": "key",
                "validatecommand": (validate_float_pos_cmd, "%P"),
            },
            right_label_text=f"[{self.unit_labels['speed']}]",
        )

        self.create_input_row(
            self.content_frame,
            row=4,
            left_label_text="Cut feedrate (Z)",
            widget_type="entry",
            widget_options={
                "default": self.defaults['cut_feed_z'],
                "width": 16,
                "validate": "key",
                "validatecommand": (validate_float_pos_cmd, "%P"),
            },
            right_label_text=f"[{self.unit_labels['speed']}]",
        )

        self.create_input_row(
            self.content_frame,
            row=5,
            left_label_text="Depth per pass",
            widget_type="entry",
            widget_options={
                "default": self.defaults['depth_per_pass'],
                "width": 16,
                "validate": "key",
                "validatecommand": (validate_float_pos_cmd, "%P"),
            },
            right_label_text=f"[{self.unit_labels['length']}]",
        )

        self.create_input_row(
            self.content_frame,
            row=6,
            left_label_text="Number of passes",
            widget_type="spinbox",
            widget_options={
                "default": self.defaults['num_passes'],
                "from_": 1,
                "to": 10,
                "increment": 1,
                "width": 8,
                "validate": "key",
                "validatecommand": (validate_passes_cmd, "%P"),
            },
            right_label_text="",
        )

        self.create_input_row(
            self.content_frame,
            row=7,
            left_label_text="Resolution",
            widget_type="spinbox",
            widget_options={
                "default": self.defaults['cut_res'],
                "from_": 100,
                "to": 5000,
                "increment": 10,
                "width": 8,
                "validate": "key",
                "validatecommand": (validate_resolution_cmd, "%P"),
            },
            right_label_text="divs/360°",
        )

        # Add an empty row for padding
        spacer = tk.Frame(self.content_frame)
        spacer.grid(row=8, column=0, columnspan=4, pady=3)  # add extra vertical padding

        # Add widgets for editing sequences
        self.sequences_lf = ttk.LabelFrame(self.main_frame, text="Sequences")
        self.sequences_lf.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.include_heading = tk.Label(self.sequences_lf, width=8, text="Include")
        self.edit_heading = tk.Label(self.sequences_lf, width=8, text="Edit")
        self.include_heading.grid(row=0, column=1, padx=5, pady=(0, 0), sticky="ew")
        self.edit_heading.grid(row=0, column=2, padx=5, pady=(0, 0), sticky="ew")

        cwd = os.getcwd()
        pencil_image = Image.open(cwd + "\\images\\" + "pencil.png")
        resized_pencil_image = pencil_image.resize((16, 16))  # resize to fit the button
        pencil_button_image = ImageTk.PhotoImage(resized_pencil_image)

        self.add_comment_label = tk.Label(self.sequences_lf, anchor="w", text="Title Comment")
        self.add_comment_var = tk.BooleanVar(value=True)
        self.add_comment_checkbutton = tk.Checkbutton(self.sequences_lf, variable=self.add_comment_var)
        self.edit_comment_button = tk.Button(self.sequences_lf, image=pencil_button_image,
                                             command=lambda: self.raise_edit_dialog("title"))

        self.add_comment_label.grid(row=1, column=0, padx=(15, 0), pady=5, sticky="w")
        self.add_comment_checkbutton.grid(row=1, column=1, sticky="ew")
        self.edit_comment_button.grid(row=1, column=2, ipadx=1, ipady=1)
        self.edit_comment_button.image = pencil_button_image  # keep a reference

        self.add_header_label = tk.Label(self.sequences_lf, anchor="w", text="Header Sequence")
        self.add_header_var = tk.BooleanVar(value=True)
        self.add_header_checkbutton = tk.Checkbutton(self.sequences_lf, variable=self.add_header_var)
        self.edit_header_button = tk.Button(self.sequences_lf, image=pencil_button_image,
                                            command=lambda: self.raise_edit_dialog("start"))

        self.add_header_label.grid(row=2, column=0, padx=(15, 0), pady=5, sticky="w")
        self.add_header_checkbutton.grid(row=2, column=1, sticky="ew")
        self.edit_header_button.grid(row=2, column=2, ipadx=1, ipady=1)
        self.edit_header_button.image = pencil_button_image  # keep a reference

        self.add_postscript_label = tk.Label(self.sequences_lf, anchor="w", text="Postscript Sequence")
        self.add_postscript_var = tk.BooleanVar(value=True)
        self.add_postscript_checkbutton = tk.Checkbutton(self.sequences_lf, variable=self.add_postscript_var)
        self.edit_postscript_button = tk.Button(self.sequences_lf, image=pencil_button_image,
                                                command=lambda: self.raise_edit_dialog("end"))

        self.add_postscript_label.grid(row=3, column=0, padx=(15, 0), pady=(5, 10), sticky="w")
        self.add_postscript_checkbutton.grid(row=3, column=1, pady=(5, 10), sticky="ew")
        self.edit_postscript_button.grid(row=3, column=2, pady=(5, 10), ipadx=1, ipady=1)
        self.edit_postscript_button.image = pencil_button_image  # keep a reference

    def get_label(self, units, measure):
        return self.label_values.get(units, {}).get(measure, "Unknown")

    def raise_edit_dialog(self, item):
        """
        Raise a dialog to enable edits to the G Code header, postscript, and tile comment sequences.
        Store the result to a variable when the dialog is cleared.

        Args:
            item (string): Keyword indicating sequence be edited ("title", "start", or "end")
        """
        dialog = EditSequenceDialog(parent=self,
                                    default_content=sseq.get_sequence(item, self.selected_units),
                                    initial_content=self.sequences[item])
        self.sequences[item] = dialog.get_settings()

    def export(self, event=None):
        toolpath_parameters = self.get_widget_values()

        title_comment = {"include": self.add_comment_var.get(),
                         "text": self.sequences['title']}

        start_sequence = {"include": self.add_header_var.get(),
                          "text": self.sequences['start']}

        end_sequence = {"include": self.add_postscript_var.get(),
                        "text": self.sequences['end']}

        self.settings = {"file_path": self.file_path,
                         "toolpath_parameters": toolpath_parameters,
                         "title_comment": title_comment,
                         "start_sequence": start_sequence,
                         "end_sequence": end_sequence
                         }

        self.close()


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
        d = ExportGCodeDialog(self, units="imperial")
        print(d.get_settings())


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
