import tkinter as tk
from tkinter import ttk


class DialogWithRows:
    def __init__(self, parent):
        self.parent = parent
        self.widgets = {}  # Store references to created widgets for easy access

    def add_row(self, parent_frame, row, left_label_text, widget_type, widget_options=None, right_label_text=None):
        """
        Create a row of GUI elements: a left label, a middle input widget, and an optional right label.

        Args:
            parent_frame (tk.Frame): The parent container to which the row will be added.
            row (int): The row index for grid placement.
            left_label_text (str): Text for the left label.
            widget_type (str): Type of middle widget ('entry', 'spinbox', or 'checkbutton').
            widget_options (dict): Options for configuring the middle widget (default: None).
            right_label_text (str): Text for the optional right label (default: None).

        Returns:
            dict: References to the created widgets (left_label, middle_widget, right_label).
        """
        # Default options for widgets
        widget_options = widget_options or {}

        # Create the left label
        left_label = tk.Label(parent_frame, text=left_label_text, width=16, anchor="e")
        left_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")

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

        elif widget_type == "checkbutton":
            var = tk.BooleanVar(value=bool(widget_options.get("default", False)))
            middle_widget = tk.Checkbutton(parent_frame, variable=var, anchor="w")
            middle_widget.grid(row=row, column=1, columnspan=2, padx=(0, 5), pady=5, sticky="w")

        else:
            raise ValueError(f"Unsupported widget_type: {widget_type}")

        # Create the optional right label
        right_label = None
        if right_label_text:
            right_label = tk.Label(parent_frame, text=right_label_text, width=16, anchor="w")
            right_label.grid(row=row, column=3, padx=5, pady=5, sticky="w")

        # Store references to widgets for external access
        self.widgets[left_label_text] = {"left_label": left_label, "middle_widget": middle_widget, "var": var, "right_label": right_label}

        return self.widgets[left_label_text]

    def get_widget_value(self, label_text):
        """
        Get the value of a widget based on the left label's text.

        Args:
            label_text (str): The text of the left label.

        Returns:
            Any: The current value of the associated widget.
        """
        widget_info = self.widgets.get(label_text)
        if not widget_info:
            return None

        var = widget_info["var"]
        if isinstance(var, (tk.StringVar, tk.BooleanVar)):
            return var.get()
        else:
            return None

    def set_widget_value(self, label_text, value):
        """
        Set the value of a widget based on the left label's text.

        Args:
            label_text (str): The text of the left label.
            value (Any): The value to set for the associated widget.
        """
        widget_info = self.widgets.get(label_text)
        if not widget_info:
            return

        var = widget_info["var"]
        if isinstance(var, (tk.StringVar, tk.BooleanVar)):
            var.set(value)


# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dynamic Rows Example")

    # Create the main frame
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill="both", expand=True)

    # Initialize the dialog
    dialog = DialogWithRows(root)

    # Add rows
    dialog.add_row(
        main_frame,
        row=0,
        left_label_text="Path Resolution",
        widget_type="spinbox",
        widget_options={
            "default": "360",
            "from_": 100,
            "to": 5000,
            "increment": 10,
        },
        right_label_text="[divs/360°]",
    )

    dialog.add_row(
        main_frame,
        row=1,
        left_label_text="Enable Feature",
        widget_type="checkbutton",
        widget_options={"default": True},
    )

    dialog.add_row(
        main_frame,
        row=2,
        left_label_text="Custom Input",
        widget_type="entry",
        widget_options={
            "default": "Default Text",
            "width": 20,
        },
    )

    # Button to display current values
    def show_values():
        for label_text in dialog.widgets.keys():
            value = dialog.get_widget_value(label_text)
            print(f"{label_text}: {value}")

    tk.Button(root, text="Show Values", command=show_values).pack(pady=10)

    root.mainloop()
