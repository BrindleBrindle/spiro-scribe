import os
import tkinter as tk
import standard_sequences as sseq
import entry_validation as ev

from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from edit_sequence_dialog import EditSequenceDialog


class ExportGCodeDialog(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        """
        Dialog to generate G Code toolpaths.

        Args:
            parent (tk.Tk): Parent tkinter application window.
        """
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("Export to G Code")
        self.resizable(False, False)
        self.transient(parent)  # keep dialog on top of main window

        # Set window to delete itself when the cancel button is pressed.
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_idletasks()

        # Position dialog at the center of the parent window.
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() / 2.0 - self.winfo_width() / 2.0,
                                      parent.winfo_rooty() + parent.winfo_height() / 2.0 - self.winfo_height() / 2.0))

        self.defaults_in = {"units": "imperial",
                            "safe_z": "0.25",
                            "jog_feed_xyz": "8.0",
                            "cut_feed_xy": "2.0",
                            "cut_feed_z": "1.0",
                            "depth_per_pass": "0.02",
                            "num_passes": 1,
                            "cut_res": 200
                            }

        self.defaults_mm = {"units": "metric",
                            "safe_z": "6.35",
                            "jog_feed_xyz": "200",
                            "cut_feed_xy": "50",
                            "cut_feed_z": "25",
                            "depth_per_pass": "0.5",
                            "num_passes": 1,
                            "cut_res": 200
                            }

        self.label_values = {
            "imperial": {
                "length": "in",
                "speed": "in/min",
            },
            "metric": {
                "length": "mm",
                "speed": "mm/min",
            },
        }

        self.settings = {}
        self.file_path = None

        # Create a frame for the main widgets
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=(5, 0))
        self.main_frame.columnconfigure(1, weight=1)

        self.toolpath_lf = ttk.LabelFrame(self.main_frame, text="Toolpath Parameters")
        self.toolpath_lf.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.selected_units = tk.StringVar(value=self.defaults_in['units'])
        self.previous_units = self.selected_units.get()
        self.units_label = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Units")
        self.units_button_in = tk.Radiobutton(self.toolpath_lf, text="in", anchor="w", variable=self.selected_units,
                                              value="imperial", command=self.on_units_selected)
        self.units_button_mm = tk.Radiobutton(self.toolpath_lf, text="mm", anchor="w", variable=self.selected_units,
                                              value="metric", command=self.on_units_selected)
        self.units_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.units_button_in.grid(row=0, column=1, sticky="ew")
        self.units_button_mm.grid(row=0, column=2, sticky="ew")

        # Register the validation function
        validate_float_cmd = self.register(ev.validate_float)
        validate_float_pos_cmd = self.register(ev.validate_float_pos)
        validate_resolution_cmd = self.register(ev.validate_resolution)
        validate_passes_cmd = self.register(ev.validate_passes)

        self.safe_Z_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Safe Z Height")
        self.safe_Z_var = tk.StringVar(value=self.defaults_in['safe_z'])
        self.safe_Z_entry = tk.Entry(self.toolpath_lf, textvariable=self.safe_Z_var,
                                     validate="key", validatecommand=(validate_float_cmd, "%P"), width=15)
        self.safe_Z_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in]")
        self.safe_Z_label_1.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.safe_Z_entry.grid(row=1, column=1, columnspan=2, sticky="ew")
        self.safe_Z_label_2.grid(row=1, column=3, padx=5, sticky="w")

        self.jog_rate_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Jog feedrate (XYZ)")
        self.jog_rate_var = tk.StringVar(value=self.defaults_in['jog_feed_xyz'])
        self.jog_rate_entry = tk.Entry(self.toolpath_lf, textvariable=self.jog_rate_var,
                                       validate="key", validatecommand=(validate_float_pos_cmd, "%P"), width=15)
        self.jog_rate_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in/min]")
        self.jog_rate_label_1.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.jog_rate_entry.grid(row=2, column=1, columnspan=2, sticky="ew")
        self.jog_rate_label_2.grid(row=2, column=3, padx=5, sticky="w")

        self.cut_rate_XY_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Cut feedrate (XY)")
        self.cut_rate_XY_var = tk.StringVar(value=self.defaults_in['cut_feed_xy'])
        self.cut_rate_XY_entry = tk.Entry(self.toolpath_lf, textvariable=self.cut_rate_XY_var,
                                          validate="key", validatecommand=(validate_float_pos_cmd, "%P"), width=15)
        self.cut_rate_XY_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in/min]")
        self.cut_rate_XY_label_1.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.cut_rate_XY_entry.grid(row=3, column=1, columnspan=2, sticky="ew")
        self.cut_rate_XY_label_2.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        self.cut_rate_Z_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Cut feedrate (Z)")
        self.cut_rate_Z_var = tk.StringVar(value=self.defaults_in['cut_feed_z'])
        self.cut_rate_Z_entry = tk.Entry(self.toolpath_lf, textvariable=self.cut_rate_Z_var,
                                         validate="key", validatecommand=(validate_float_pos_cmd, "%P"), width=15)
        self.cut_rate_Z_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in/min]")
        self.cut_rate_Z_label_1.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.cut_rate_Z_entry.grid(row=4, column=1, columnspan=2, sticky="ew")
        self.cut_rate_Z_label_2.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        self.depth_per_pass_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Depth per pass")
        self.depth_per_pass_var = tk.StringVar(value=self.defaults_in['depth_per_pass'])
        self.depth_per_pass_entry = tk.Entry(self.toolpath_lf, textvariable=self.depth_per_pass_var,
                                             validate="key", validatecommand=(validate_float_pos_cmd, "%P"), width=15)
        self.depth_per_pass_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in]")
        self.depth_per_pass_label_1.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.depth_per_pass_entry.grid(row=5, column=1, columnspan=2, sticky="ew")
        self.depth_per_pass_label_2.grid(row=5, column=3, padx=5, pady=5, sticky="w")

        self.num_passes_label = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Number of passes")
        self.num_passes_var = tk.StringVar(value=1)
        self.num_passes_spinbox = tk.Spinbox(self.toolpath_lf, from_=1, to=10, increment=1, width=8,
                                             validate="key", validatecommand=((validate_passes_cmd, "%P")),
                                             textvariable=self.num_passes_var)
        self.num_passes_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.num_passes_spinbox.grid(row=6, column=1, columnspan=2, sticky="ew")

        self.res_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Resolution")
        self.res_var = tk.StringVar(value=self.defaults_in['cut_res'])
        self.res_spinbox = tk.Spinbox(self.toolpath_lf, from_=100, to=5000, increment=10, width=8,
                                      validate="key", validatecommand=((validate_resolution_cmd, "%P")),
                                      textvariable=self.res_var)
        self.res_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[divs/360°]")
        self.res_label_1.grid(row=7, column=0, padx=5, pady=(5, 10), sticky="w")
        self.res_spinbox.grid(row=7, column=1, columnspan=2, sticky="ew")
        self.res_label_2.grid(row=7, column=3, padx=5, pady=5, sticky="w")

        self.sequences_lf = ttk.LabelFrame(self.main_frame, text="Sequences")
        self.sequences_lf.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        self.sequences_lf.columnconfigure(0, weight=1)

        self.include_heading = tk.Label(self.sequences_lf, width=8, text="Include")
        self.edit_heading = tk.Label(self.sequences_lf, width=8, text="Edit")
        self.include_heading.grid(row=0, column=1, padx=5, pady=(0, 0), sticky="ew")
        self.edit_heading.grid(row=0, column=2, padx=5, pady=(0, 0), sticky="ew")

        cwd = os.getcwd()
        pencil_image = Image.open(cwd + "\\images\\" + "pencil.png")
        resized_pencil_image = pencil_image.resize((16, 16))  # Resize to fit the button
        pencil_button_image = ImageTk.PhotoImage(resized_pencil_image)

        self.add_comment_label = tk.Label(self.sequences_lf, anchor="w", text="Description (title comment)")
        self.add_comment_var = tk.BooleanVar(value=True)
        self.add_comment_checkbutton = tk.Checkbutton(self.sequences_lf, variable=self.add_comment_var)
        self.edit_comment_button = tk.Button(self.sequences_lf, image=pencil_button_image,
                                             command=lambda: self.raise_edit_dialog("title"))

        self.add_comment_label.grid(row=1, column=0, padx=(5, 0), pady=5, sticky="w")
        self.add_comment_checkbutton.grid(row=1, column=1, sticky="ew")
        self.edit_comment_button.grid(row=1, column=2, ipadx=1, ipady=1)
        self.edit_comment_button.image = pencil_button_image  # Keep a reference

        self.add_header_label = tk.Label(self.sequences_lf, anchor="w", text="Start sequence (header)")
        self.add_header_var = tk.BooleanVar(value=True)
        self.add_header_checkbutton = tk.Checkbutton(self.sequences_lf, variable=self.add_header_var)
        self.edit_header_button = tk.Button(self.sequences_lf, image=pencil_button_image,
                                            command=lambda: self.raise_edit_dialog("start"))

        self.add_header_label.grid(row=2, column=0, padx=(5, 0), pady=5, sticky="w")
        self.add_header_checkbutton.grid(row=2, column=1, sticky="ew")
        self.edit_header_button.grid(row=2, column=2, ipadx=1, ipady=1)
        self.edit_header_button.image = pencil_button_image  # Keep a reference

        self.add_postscript_label = tk.Label(self.sequences_lf, anchor="w", text="End sequence (postscript)")
        self.add_postscript_var = tk.BooleanVar(value=True)
        self.add_postscript_checkbutton = tk.Checkbutton(self.sequences_lf, variable=self.add_postscript_var)
        self.edit_postscript_button = tk.Button(self.sequences_lf, image=pencil_button_image,
                                                command=lambda: self.raise_edit_dialog("end"))

        self.add_postscript_label.grid(row=3, column=0, padx=(5, 0), pady=(5, 10), sticky="w")
        self.add_postscript_checkbutton.grid(row=3, column=1, pady=(5, 10), sticky="ew")
        self.edit_postscript_button.grid(row=3, column=2, pady=(5, 10), ipadx=1, ipady=1)
        self.edit_postscript_button.image = pencil_button_image  # Keep a reference

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

        # Generate starting sequences
        self.title_comment = sseq.get_example_title(self.selected_units.get())
        self.start_sequence = sseq.get_start_sequence(self.selected_units.get())
        self.end_sequence = sseq.get_end_sequence()

        # Make dialog visible and set the widget that has focus.
        self.deiconify()
        self.focus_set()
        self.wait_visibility()

        # Direct all events to this window and its descendents.
        self.grab_set()

        # Stop main script until dialog is dismissed.
        self.wait_window(self)

    def get_label(self, units, measure):
        return self.label_values.get(units, {}).get(measure, "Unknown")

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

    def round_float(self, value, N):
        """
        Rounds a float value to the specified number of decimal places.

        Args:
            value (float): Value to round.
            N (int): Number of decimal places to use for rounding.

        Returns:
            float: The rounded value to N decimal places.
        """
        return round(value, N)

    def on_units_selected(self):
        """
        Callback method called when unit radio button is selected.

        Args:
            None

        Returns:
            None
        """
        units = self.selected_units.get()
        units_changed = True if units != self.previous_units else False

        # Update unit labels.
        self.safe_Z_label_2["text"] = f"[{self.get_label(units, "length")}]"
        self.jog_rate_label_2["text"] = f"[{self.get_label(units, "speed")}]"
        self.cut_rate_XY_label_2["text"] = f"[{self.get_label(units, "speed")}]"
        self.cut_rate_Z_label_2["text"] = f"[{self.get_label(units, "speed")}]"
        self.depth_per_pass_label_2["text"] = f"[{self.get_label(units, "length")}]"

        # Convert field values if unit system changed.
        if units_changed:
            # Convert safe Z height.
            safe_Z_entry = self.safe_Z_var.get()
            if safe_Z_entry:
                safe_Z = self.convert_value(float(safe_Z_entry), units)
                safe_Z_rounded = self.round_float(safe_Z, 4)
                self.safe_Z_var.set(safe_Z_rounded)  # insert new text
                self.safe_Z_entry.icursor(tk.END)  # move cursor to end of line

            # Convert jog feedrate.
            jog_rate_entry = self.jog_rate_var.get()
            if jog_rate_entry:
                jog_rate = self.convert_value(float(jog_rate_entry), units)
                jog_rate_rounded = self.round_float(jog_rate, 4)
                self.jog_rate_var.set(jog_rate_rounded)  # insert new text
                self.jog_rate_entry.icursor(tk.END)  # move cursor to end of line

            # Convert cut feedrate (XY).
            cut_rate_XY_entry = self.cut_rate_XY_var.get()
            if cut_rate_XY_entry:
                cut_rate_XY = self.convert_value(float(cut_rate_XY_entry), units)
                cut_rate_XY_rounded = self.round_float(cut_rate_XY, 4)
                self.cut_rate_XY_var.set(cut_rate_XY_rounded)  # insert new text
                self.cut_rate_XY_entry.icursor(tk.END)  # move cursor to end of line

            # Convert cut feedrate (Z).
            cut_rate_Z_entry = self.cut_rate_Z_var.get()
            if cut_rate_Z_entry:
                cut_rate_Z = self.convert_value(float(cut_rate_Z_entry), units)
                cut_rate_Z_rounded = self.round_float(cut_rate_Z, 4)
                self.cut_rate_Z_var.set(cut_rate_Z_rounded)  # insert new text
                self.cut_rate_Z_entry.icursor(tk.END)  # move cursor to end of line

            # Convert depth per pass.
            depth_per_pass_entry = self.depth_per_pass_var.get()
            if depth_per_pass_entry:
                depth_per_pass = self.convert_value(float(depth_per_pass_entry), units)
                depth_per_pass_rounded = self.round_float(depth_per_pass, 4)
                self.depth_per_pass_var.set(depth_per_pass_rounded)  # insert new text
                self.depth_per_pass_entry.icursor(tk.END)  # move cursor to end of line

            self.previous_units = units

    def raise_edit_dialog(self, item):
        """
        Raise a dialog to enable edits to the G Code header, postscript, and tile comment sequences.
        Store the result to a variable when the dialog is cleared.

        Args:
            item (string): Keyword indicating which sequence is to be edited;
                           acceptable values: "title", "start", "end"

        Returns:
            None
        """
        units = self.selected_units.get()

        if item == "title":
            dialog = EditSequenceDialog(self, default_content=sseq.get_example_title(units),
                                        initial_content=self.title_comment)
            self.title_comment = dialog.get_settings()
        elif item == "start":
            dialog = EditSequenceDialog(self, default_content=sseq.get_start_sequence(units),
                                        initial_content=self.start_sequence)
            self.start_sequence = dialog.get_settings()
        elif item == "end":
            dialog = EditSequenceDialog(self, default_content=sseq.get_end_sequence(),
                                        initial_content=self.end_sequence)
            self.end_sequence = dialog.get_settings()

    def raise_save_as_dialog(self):
        file_path = filedialog.asksaveasfilename(title="Select Output Location",
                                                 defaultextension=".gcode", 
                                                 filetypes=[("G-Code File", "*.nc")],
                                                 initialdir=os.getcwd())

        if file_path:
            self.export_button.configure(state='normal')
            self.out_location_var.set(file_path)
            self.file_path = file_path

    def export(self, event=None):
        toolpath_parameters = {}
        toolpath_parameters['units'] = self.selected_units.get()
        toolpath_parameters['safe_z'] = float(self.safe_Z_var.get())
        toolpath_parameters['jog_feed_xyz'] = float(self.jog_rate_var.get())
        toolpath_parameters['cut_feed_xy'] = float(self.cut_rate_XY_var.get())
        toolpath_parameters['cut_feed_z'] = float(self.cut_rate_Z_var.get())
        toolpath_parameters['depth_per_pass'] = float(self.depth_per_pass_var.get())
        toolpath_parameters['num_passes'] = int(self.num_passes_var.get())
        toolpath_parameters['cut_res'] = int(self.res_var.get())

        title_comment = {}
        title_comment['include'] = self.add_comment_var.get()
        title_comment['text'] = self.title_comment

        start_sequence = {}
        start_sequence['include'] = self.add_header_var.get()
        start_sequence['text'] = self.start_sequence

        end_sequence = {}
        end_sequence['include'] = self.add_postscript_var.get()
        end_sequence['text'] = self.end_sequence

        self.settings = {"file_path": self.file_path,
                         "toolpath_parameters": toolpath_parameters,
                         "title_comment": title_comment,
                         "start_sequence": start_sequence,
                         "end_sequence": end_sequence
                         }

        self.close()

    def cancel(self, event=None):
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
        ExportGCodeDialog(self)


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
