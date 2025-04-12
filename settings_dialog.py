import tkinter as tk
from tkinter import colorchooser


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, initial_color="#FFFFFF", show_origin=True, origin_position=(1, 1), *args, **kwargs):
        """
        Dialog to configure settings.

        Args:
            parent (tk.Tk): Parent window.
            initial_color (str): Current background color.
            show_origin (bool): Current display status of the origin marker (on/off).
            origin_position (tuple): Current origin position (row, column).
        """
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("Settings")
        self.resizable(False, False)
        self.transient(parent)  # keep dialog on top of main window

        # Store the passed-in initial values
        self.current_color = initial_color
        self.show_origin_state = show_origin
        self.origin_position = origin_position

        # Set window to delete itself when the cancel button is pressed.
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.update_idletasks()

        # Position dialog at the center of the parent window.
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() / 2.0 - self.winfo_width() / 2.0,
                                      parent.winfo_rooty() + parent.winfo_height() / 2.0 - self.winfo_height() / 2.0))

        # Create a frame for the label and the buttons
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=5)

        # Add the color picker widget
        self.color_picker_label = tk.Label(self.main_frame, text="Background Color:")
        self.color_picker_label.grid(row=0, column=0, padx=0, pady=10, sticky="w")

        # Create a small square to display the selected color with a subtle border
        self.color_display = tk.Canvas(
            self.main_frame,
            width=20,
            height=20,
            bg=self.current_color,  # initialize with passed-in color
            highlightthickness=1,  # subtle border thickness
            highlightbackground="gray"  # subtle border color
        )
        self.color_display.grid(row=0, column=1, padx=4, pady=10, sticky="w")

        # Bind a click event to open the color picker
        self.color_display.bind("<Button-1>", self.open_color_picker)

        # Add a CheckButton for toggling origin marker on/off.
        self.show_origin_label = tk.Label(self.main_frame, text="Show Origin:")
        self.show_origin_label.grid(row=1, column=0, padx=0, pady=0, sticky="w")
        self.show_origin_var = tk.BooleanVar(value=self.show_origin_state)  # initialize with passed-in value
        self.show_origin_button = tk.Checkbutton(self.main_frame, variable=self.show_origin_var)
        self.show_origin_button.grid(row=1, column=1, padx=0, pady=0, sticky="w")

        # Add the label to the left of the buttons
        self.origin_position_label = tk.Label(self.main_frame, text="Origin Position:")
        self.origin_position_label.grid(row=3, column=0, padx=0, pady=10, sticky="w")

        # Create the 3x3 grid of buttons
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.grid(row=3, column=1, padx=0, pady=10, sticky="w")

        # Dictionary to store button references
        self.buttons = {}

        # Create a 3x3 grid of buttons
        arrows = ["↖", "↑", "↗", "←", "•", "→", "↙", "↓", "↘"]
        for i in range(3):
            for j in range(3):
                button = tk.Button(
                    self.button_frame,
                    text=arrows[i * 3 + j],
                    font=("Arial", 10),
                    width=2,
                    height=1,
                    relief="sunken" if (i, j) == self.origin_position else "raised",  # preselect button
                    command=lambda b=(i, j): self.toggle_button(b)  # pass button position
                )
                button.grid(row=i, column=j, padx=2, pady=2)
                self.buttons[(i, j)] = button  # store a reference to the button

        # Add a close button
        self.apply_button = tk.Button(self, text="Apply", command=self.close)
        self.apply_button.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="nsew")
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

    def open_color_picker(self, event):
        """Open a color picker dialog and update the color display."""
        # Open the color picker with the current color pre-selected
        color_code = colorchooser.askcolor(color=self.current_color, title="Choose a color")[1]  # get the color hex code
        if color_code:  # if a color is selected, update the square's background
            self.current_color = color_code  # store the new color
            self.color_display.config(bg=color_code)
            self.event_generate("<<BackgroundColorAction>>")  # notify parent of new color

    def toggle_button(self, button_id):
        """
        Toggle the visual state of the button.
        Ensure only one button can be in the sunken (depressed) state.
        """
        # If a button is already selected, reset it to normal
        if self.origin_position is not None:
            prev_button = self.buttons[self.origin_position]
            prev_button.config(relief="raised")

        # Set the new button to sunken state
        new_button = self.buttons[button_id]
        new_button.config(relief="sunken")

        # Update the currently selected button
        self.origin_position = button_id

    def get_settings(self):
        """Return the current state of the dialog widgets."""
        return {
            "bg_color": self.current_color,
            "show_origin": self.show_origin_var.get(),
            "origin_position": self.origin_position
        }


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
        bg_color = "#FF0000"
        show_origin = True
        origin_position = (0, 1)  # top-center button
        dialog = SettingsDialog(self,
                                initial_color=bg_color,
                                show_origin=show_origin,
                                origin_position=origin_position
                                )
        settings = dialog.get_settings()
        print(settings)


# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
