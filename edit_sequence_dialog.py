import tkinter as tk


class EditSequenceDialog(tk.Toplevel):
    def __init__(self, parent, initial_content="", *args, **kwargs):
        """
        Dialog to configure sequence text.

        Args:
            parent (tk.Tk): Parent window.
            content (str): Current content.
        """
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("Edit Sequence Text")
        self.resizable(False, False)
        self.transient(parent)  # keep dialog on top of main window

        # Store the passed-in initial values
        self.content = initial_content

        # Set window to delete itself when the cancel button is pressed.
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.update_idletasks()

        # Position dialog at the center of the parent window.
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() / 2.0 - self.winfo_width() / 2.0,
                                      parent.winfo_rooty() + parent.winfo_height() / 2.0 - self.winfo_height() / 2.0))

        # Create a frame for the label and the buttons
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=5)

        # Multi-line Textbox with Scrollbar
        self.textbox = tk.Text(self.main_frame, width=40, height=10, wrap=tk.WORD)
        self.textbox.grid(row=0, column=0, sticky="nsew", pady=5)

        self.scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.textbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

        self.textbox.config(yscrollcommand=self.scrollbar.set)

        # Set default text in the textbox
        self.textbox.insert("1.0", self.content)

        self.button_frame = tk.Frame(self.main_frame)
        # self.button_frame.columnconfigure(0, weight=0)
        self.button_frame.columnconfigure(1, weight=1)
        # self.button_frame.columnconfigure(2, weight=0)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="nsew")

        # Restore Default button
        self.restore_button = tk.Button(self.button_frame, text="Restore Default", command=self.restore_default)
        self.restore_button.grid(row=0, column=0, padx=5, sticky="w")

        # Cancel button
        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=0, column=1, padx=5, sticky="e")

        # OK button
        self.ok_button = tk.Button(self.button_frame, text="OK", command=self.ok, default=tk.ACTIVE)
        self.ok_button.grid(row=0, column=2, padx=5, sticky="e")

        # self.bind("<Return>", self.close)

        # Make dialog visible and set the widget that has focus.
        self.deiconify()
        self.focus_set()
        self.wait_visibility()

        # Direct all events to this window and its descendents.
        self.grab_set()

        # Stop main script until dialog is dismissed.
        self.wait_window(self)

    def restore_default(self):
        pass

    def ok(self):
        pass

    def cancel(self):
        pass

    def close(self, event=None):
        """Return focus to the parent window and close."""
        if self.parent is not None:
            self.parent.focus_set()
        tk.Toplevel.destroy(self)

    def get_settings(self):
        """Return the current content of the dialog."""
        return self.content


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
        # Pass in initial values for the dialog
        test_content = "Lorem ipsum..."
        dialog = EditSequenceDialog(self, initial_content=test_content)
        settings = dialog.get_settings()
        print(settings)


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
