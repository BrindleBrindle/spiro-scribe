import tkinter as tk
import standard_sequences as sseq


class EditSequenceDialog(tk.Toplevel):
    def __init__(self, parent, default_content="", initial_content="", *args, **kwargs):
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

        self.new_content = ""
        self.default_content = default_content
        self.initial_content = initial_content

        # Set window to delete itself when the cancel button is pressed.
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_idletasks()

        # Position dialog at the center of the parent window.
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() / 2.0 - self.winfo_width() / 2.0,
                                      parent.winfo_rooty() + parent.winfo_height() / 2.0 - self.winfo_height() / 2.0))

        # Create a frame for the label and the buttons
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=5)

        # Multi-line Textbox with Scrollbar
        self.textbox = tk.Text(self.main_frame, width=70, height=10, wrap=tk.WORD)
        self.textbox.grid(row=0, column=0, sticky="nsew", pady=5)

        self.scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.textbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns", pady=5)

        self.textbox.config(yscrollcommand=self.scrollbar.set)

        # Set starting text in the textbox
        self.textbox.insert("1.0", self.initial_content)

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="nsew")

        # Refresh button
        if self.initial_content == self.default_content:
            refresh_button_state = tk.DISABLED
        else:
            refresh_button_state = tk.NORMAL
        self.refresh_button = tk.Button(self.button_frame, text="Refresh",
                                        state=refresh_button_state, command=self.refresh)
        self.refresh_button.grid(row=0, column=0, padx=5, sticky="w")

        # Cancel button
        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=0, column=1, padx=5, sticky="e")

        # OK button
        self.ok_button = tk.Button(self.button_frame, text="OK", command=self.ok, default=tk.ACTIVE)
        self.ok_button.grid(row=0, column=2, padx=5, sticky="e")

        # Bind the <<Modified>> event to the Text widget.
        self.textbox.bind("<<Modified>>", self.on_text_change)
        self.textbox.edit_modified(False)  # reset the modified flag

        # Bind the <Return> event to the whole application.
        self.bind("<Return>", self.ok)

        # Make dialog visible and set the widget that has focus.
        self.deiconify()
        self.focus_set()
        self.wait_visibility()

        # Direct all events to this window and its descendents.
        self.grab_set()

        # Stop main script until dialog is dismissed.
        self.wait_window(self)

    def on_text_change(self, event):
        """
        Re-enables the Refresh button when the Text widget content is modified.
        """
        # Enable the button only if the content has been modified
        if self.textbox.edit_modified():
            self.refresh_button.config(state=tk.NORMAL)
            self.textbox.edit_modified(False)  # Reset the modified flag

    def refresh(self):
        """
        Restores the default content in the Text widget and disables the button.
        """
        # Reset the <<Modified>> event flag.
        self.textbox.edit_modified(False)

        # Update the Text widget contents.
        self.textbox.delete("1.0", tk.END)
        self.textbox.insert("1.0", self.default_content)

        # Disable the button.
        self.refresh_button.configure(state=tk.DISABLED)

        # Ensure the modified flag is still reset.
        self.textbox.edit_modified(False)

    def ok(self, event=None):
        self.new_content = self.textbox.get("1.0", tk.END).strip()
        self.close()

    def cancel(self, event=None):
        self.new_content = self.initial_content
        self.close()

    def close(self, event=None):
        """Return focus to the parent window and close."""
        if self.parent is not None:
            self.parent.focus_set()
        tk.Toplevel.destroy(self)

    def get_settings(self):
        """
        Return the final content of the Text widget.
        """
        return self.new_content


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
        test_init_content = "Hello!"
        test_default_content = sseq.get_example_title("imperial")
        dialog = EditSequenceDialog(self, default_content=test_default_content, initial_content=test_init_content)
        settings = dialog.get_settings()
        print(settings)


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
