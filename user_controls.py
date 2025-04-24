import tkinter as tk
from tkinter import ttk
from circle_settings import CircleSettings
from roulette_settings import RouletteSettings


class UserControlsPane(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create a Notebook widget
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")  # Use grid for layout

        # Configure this frame (TabbedPane) to stretch with the parent
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create tabs
        self.create_tabs()

       # Bind the Notebook to remove focus whenever a new tab is selected
        self.notebook.bind("<<NotebookTabChanged>>", self.set_focus_to_tab)

    def set_focus_to_tab(tab, event=None):
        """Remove focus from all widgets in tab."""
        tab.focus()  # set focus to the tab (or another non-interactive widget)

    def create_tabs(self):
        """Create two tabs and add them to the Notebook."""
        # Tab 1
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="Simple Circles")

        circle_settings = CircleSettings(tab1)
        circle_settings.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        # Tab 2
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="Roulettes")

        roulette_settings = RouletteSettings(tab2)
        roulette_settings.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")


# Main application demonstrating how to embed the class in an application.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("User Controls Pane")
    root.resizable(False, False)  # prevent resizing in both width and height

    # Configure the root grid to stretch with resizing
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Embed ControlsPane class inside the main window
    tabbed_pane = UserControlsPane(root)
    tabbed_pane.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # Use grid to center and expand

    # Run the application
    root.mainloop()
