import tkinter as tk


class InfoDialog(tk.Toplevel):
    def __init__(self, parent, text_list, *args, **kwargs):
        """
        Dialog to show program details.

        Args:
            parent (tk.Tk): Parent window.
            text_list (str): Text to display in dialog.
        """
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("About SpiroScribe")
        self.resizable(False, False)
        self.transient(parent)  # keep dialog on top of main window

        # Set window to delete itself when the close button is pressed
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.update_idletasks()

        # Position dialog at the center of the parent window.
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() / 2.0 - self.winfo_width() / 2.0,
                                      parent.winfo_rooty() + parent.winfo_height() / 2.0 - self.winfo_height() / 2.0))

        # Create a frame for the label and the buttons
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=5)

        # Add the heading (first entry in the list)
        heading = tk.Label(
            self.main_frame,
            text=text_list[0],  # first entry is the heading
            font=("Arial", 12, "bold"),
            pady=10
        )
        heading.grid(row=0, column=0, pady=(10, 5))  # place heading in the first row

        # Add the remaining entries as labels
        for idx, entry in enumerate(text_list[1:], start=1):
            label = tk.Label(
                self.main_frame,
                text=entry,
                anchor="w",
                justify="left",
                wraplength=350  # wrap text to fit the dialog width
            )
            label.grid(row=idx, column=0, sticky="w", padx=10, pady=5)  # align labels to the left

        # Add an OK button
        ok_button = tk.Button(
            self.main_frame,
            text="OK",
            command=self.close,
            padx=10, pady=5
        )
        ok_button.grid(row=len(text_list), column=0, pady=(15, 10))  # place below the labels
        self.bind("<Return>", self.close)

        # Make dialog visible and set the widget that has focus.
        self.deiconify()
        self.focus_set()
        self.wait_visibility()

        # Direct all events to this window and its descendents.
        self.grab_set()

        # Stop main script until dialog is dismissed.
        self.wait_window(self)

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
        text_list = [
            "A Celebration of Love and Friendship",  # heading
            "This application was created to celebrate our wedding on September 19th, 2025."
            ]
        dialog = InfoDialog(self, text_list)


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
