import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from edit_sequence_dialog import EditSequenceDialog


class ExportGCodeDialog(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        """
        Dialog to generate G Code toolpaths.

        Args:
            TODO
        """
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("Export to G Code")
        self.resizable(False, False)
        self.transient(parent)  # keep dialog on top of main window

        # Set window to delete itself when the cancel button is pressed.
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.update_idletasks()

        # Position dialog at the center of the parent window.
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() / 2.0 - self.winfo_width() / 2.0,
                                      parent.winfo_rooty() + parent.winfo_height() / 2.0 - self.winfo_height() / 2.0))

        # self.configure(bg="gray90")

        # Create a frame for the main widgets
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=(5, 0))
        self.main_frame.columnconfigure(1, weight=1)

        self.toolpath_lf = ttk.LabelFrame(self.main_frame, text="Toolpath Parameters")
        self.toolpath_lf.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.unit_var = tk.StringVar(value="in")
        self.units_label = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Units")
        self.units_button_in = tk.Radiobutton(self.toolpath_lf, text="in", anchor="w", variable=self.unit_var, value="in")
        self.units_button_mm = tk.Radiobutton(self.toolpath_lf, text="mm", anchor="w", variable=self.unit_var, value="mm")
        self.units_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.units_button_in.grid(row=0, column=1, sticky="ew")
        self.units_button_mm.grid(row=0, column=2, sticky="ew")

        self.safe_Z_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Safe Z Height")
        self.safe_Z_entry = tk.Entry(self.toolpath_lf, text="")
        self.safe_Z_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in]")
        self.safe_Z_label_1.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.safe_Z_entry.grid(row=1, column=1, columnspan=2, sticky="ew")
        self.safe_Z_label_2.grid(row=1, column=3, padx=5, sticky="w")

        self.jog_rate_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Jog feedrate (XYZ)")
        self.jog_rate_entry = tk.Entry(self.toolpath_lf, width=15, text="")
        self.jog_rate_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in/min]")
        self.jog_rate_label_1.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.jog_rate_entry.grid(row=2, column=1, columnspan=2, sticky="ew")
        self.jog_rate_label_2.grid(row=2, column=3, padx=5, sticky="w")

        self.cut_rate_XY_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Cut feedrate (XY)")
        self.cut_rate_XY_entry = tk.Entry(self.toolpath_lf, width=15, text="")
        self.cut_rate_XY_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in/min]")
        self.cut_rate_XY_label_1.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.cut_rate_XY_entry.grid(row=3, column=1, columnspan=2, sticky="ew")
        self.cut_rate_XY_label_2.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        self.cut_rate_Z_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Cut feedrate (Z)")
        self.cut_rate_Z_entry = tk.Entry(self.toolpath_lf, width=15, text="")
        self.cut_rate_Z_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in/min]")
        self.cut_rate_Z_label_1.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.cut_rate_Z_entry.grid(row=4, column=1, columnspan=2, sticky="ew")
        self.cut_rate_Z_label_2.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        self.depth_per_pass_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Depth per pass")
        self.depth_per_pass_entry = tk.Entry(self.toolpath_lf, width=15, text="")
        self.depth_per_pass_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="[in]")
        self.depth_per_pass_label_1.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.depth_per_pass_entry.grid(row=5, column=1, columnspan=2, sticky="ew")
        self.depth_per_pass_label_2.grid(row=5, column=3, padx=5, pady=5, sticky="w")

        self.num_passes_label = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Number of passes")
        self.num_passes_var = tk.StringVar(value=1)
        self.num_passes_spinbox = tk.Spinbox(self.toolpath_lf, from_=1, to=10, increment=1, width=8, state="readonly", textvariable=self.num_passes_var)
        self.num_passes_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.num_passes_spinbox.grid(row=6, column=1, columnspan=2, sticky="w")

        self.arc_res_label_1 = tk.Label(self.toolpath_lf, width=16, anchor="e", text="Arc resolution")
        self.arc_res_slider = tk.Scale(self.toolpath_lf, from_=0, to=100, orient="horizontal", showvalue=False)
        self.arc_res_label_2 = tk.Label(self.toolpath_lf, width=16, anchor="w", text="100")
        self.arc_res_label_1.grid(row=7, column=0, padx=5, pady=(5, 10), sticky="w")
        self.arc_res_slider.grid(row=7, column=1, columnspan=2, sticky="ew")
        self.arc_res_label_2.grid(row=7, column=3, sticky="w")

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
        self.add_comment_var = tk.BooleanVar(value=False)
        self.add_comment_checkbutton = tk.Checkbutton(self.sequences_lf, variable=self.add_comment_var)
        self.edit_comment_button = tk.Button(self.sequences_lf, image=pencil_button_image, command=self.raise_edit_dialog)

        self.add_comment_label.grid(row=1, column=0, padx=(5, 0), pady=5, sticky="w")
        self.add_comment_checkbutton.grid(row=1, column=1, sticky="ew")
        self.edit_comment_button.grid(row=1, column=2, ipadx=1, ipady=1)
        self.edit_comment_button.image = pencil_button_image  # Keep a reference

        self.add_header_label = tk.Label(self.sequences_lf, anchor="w", text="Start sequence (header)")
        self.add_header_var = tk.BooleanVar(value=False)
        self.add_header_checkbutton = tk.Checkbutton(self.sequences_lf, variable=self.add_header_var)
        self.edit_header_button = tk.Button(self.sequences_lf, image=pencil_button_image, command=self.raise_edit_dialog)

        self.add_header_label.grid(row=2, column=0, padx=(5, 0), pady=5, sticky="w")
        self.add_header_checkbutton.grid(row=2, column=1, sticky="ew")
        self.edit_header_button.grid(row=2, column=2, ipadx=1, ipady=1)
        self.edit_header_button.image = pencil_button_image  # Keep a reference

        self.add_postscript_label = tk.Label(self.sequences_lf, anchor="w", text="End sequence (postscript)")
        self.add_postscript_var = tk.BooleanVar(value=False)
        self.add_postscript_checkbutton = tk.Checkbutton(self.sequences_lf, variable=self.add_postscript_var)
        self.edit_postscript_button = tk.Button(self.sequences_lf, image=pencil_button_image, command=self.raise_edit_dialog)

        self.add_postscript_label.grid(row=3, column=0, padx=(5, 0), pady=(5, 10), sticky="w")
        self.add_postscript_checkbutton.grid(row=3, column=1, pady=(5, 10), sticky="ew")
        self.edit_postscript_button.grid(row=3, column=2, pady=(5, 10), ipadx=1, ipady=1)
        self.edit_postscript_button.image = pencil_button_image  # Keep a reference

        folder_image = Image.open(cwd + "\\images\\" + "folder.png")
        resized_folder_image = folder_image.resize((18, 18))  # Resize to fit the button
        folder_button_image = ImageTk.PhotoImage(resized_folder_image)

        self.out_location_label = tk.Label(self.main_frame, anchor="w", text="Output location")
        self.out_location_entry = tk.Entry(self.main_frame, state="disabled", text="")
        self.out_location_button = tk.Button(self.main_frame, anchor="w", image=folder_button_image)
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
        self.export_button = tk.Button(self.export_button_frame, text="Export", command=self.close)
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

    def raise_edit_dialog(self):
        # Pass in initial values for the dialog
        test_content = "Lorem ipsum..."
        dialog = EditSequenceDialog(self, initial_content=test_content)
        settings = dialog.get_settings()
        print(settings)

    def close(self, event=None):
        """Return focus to the parent window and close."""
        if self.parent is not None:
            self.parent.focus_set()
        tk.Toplevel.destroy(self)


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
