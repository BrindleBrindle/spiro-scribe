import tkinter as tk
import os
from user_controls import UserControlsPane
from preview_canvas import PreviewCanvas
from gcode_post_processor import GCodePostProcessor
from svg_post_processor import SVGPostProcessor
from settings_dialog import SettingsDialog
from info_dialog import InfoDialog
from status_bar import StatusBar
from export_svg_dialog import ExportSVGDialog
from export_gcode_dialog import ExportGCodeDialog
from PIL import Image, ImageTk


class SpiroScribeApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        """
        Initialize the SpiroScribeApp.

        Arguments:
            None

        Returns:
            None
        """
        super().__init__(*args, **kwargs)  # pass arguments to tk.Tk

        self.title("SpiroScribe")
        self.resizable(False, False)  # prevent resizing (width and height)

        self.origin_position = (1, 1)
        self.workspace_dims = (32, 32)
        self.workspace_units = "mm"

        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.menu_frame = tk.Frame(self.frame)
        self.menu_frame.grid_columnconfigure(0, weight=0)
        self.menu_frame.grid_columnconfigure(1, weight=0)
        self.menu_frame.grid_columnconfigure(2, weight=1)
        self.menu_frame.grid_columnconfigure(3, weight=0)
        self.menu_frame.grid(row=0, column=0, padx=(10, 10), pady=(5, 5), sticky="nsew")

        self.export_svg_button = tk.Button(self.menu_frame, text="Export to SVG", command=self.open_export_svg_dialog)
        self.export_svg_button.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

        self.export_gcode_button = tk.Button(self.menu_frame, text="Export to G Code",
                                             command=self.open_export_gcode_dialog)
        self.export_gcode_button.grid(row=0, column=1, padx=(5, 5), sticky="nsew")

        self.settings_button = tk.Button(self.menu_frame, text="Settings", command=self.open_settings_dialog)
        self.settings_button.grid(row=0, column=2, padx=(5, 5), sticky="nsw")

        cwd = os.getcwd()
        image = Image.open(cwd + "\\images\\" + "info.png")
        resized_image = image.resize((24, 24))  # resize to fit the button
        button_image = ImageTk.PhotoImage(resized_image)
        self.info_button = tk.Button(self.menu_frame, image=button_image, command=self.open_info_dialog)
        self.info_button.grid(row=0, column=3, padx=(5, 0), sticky="e")

        # Keep a reference to the image to prevent garbage collection
        self.info_button.image = button_image

        self.circles = []
        self.roulette = {}

        self.canvas = PreviewCanvas(
            parent=self.frame,
            width=400,
            height=400,
            mm_to_px_ratio=15,
        )
        self.canvas.grid(row=1, column=0, padx=(5, 5), pady=(0, 0))

        self.status_bar = StatusBar(self.frame, self.canvas, width_mm=32, height_mm=32, width_px=400)
        self.status_bar.grid(row=2, column=0, padx=(6, 6), sticky="ew")

        self.user_controls = UserControlsPane(self.frame)
        self.user_controls.grid(row=3, column=0, padx=(5, 5), pady=(10, 5), sticky="nsew")

        # Bind to widget custom events
        self.bind("<<BackgroundColorAction>>", self.handle_background_color_event)
        self.bind("<<PatternLinewidthAction>>", self.handle_pattern_lw_event)
        self.bind("<<UpdateCircleAction>>", self.handle_update_circle_event)
        self.bind("<<UpdateRouletteAction>>", self.handle_update_roulette_event)

        self.canvas.refresh_pattern()

    def open_export_svg_dialog(self):
        # Open Export SVG dialog.
        dialog = ExportSVGDialog(self)

        # Retrieve settings from dialog.
        export_settings = dialog.get_settings()

        # Add workspace settings.
        export_settings['svg_parameters']['workspace_width'] = self.workspace_dims[0]
        export_settings['svg_parameters']['workspace_height'] = self.workspace_dims[1]
        export_settings['svg_parameters']['workspace_units'] = self.workspace_units

        # Export SVG file if settings are not empty.
        if export_settings:
            # Initialize instance of SVG post processor.
            post_processor = SVGPostProcessor(export_settings['svg_parameters'])

            # Add roulette (if specified).
            if self.roulette:
                post_processor.parse_pattern(self.roulette)

        # Export SVG to file.
        post_processor.save_to_file(export_settings['file_path'])

    def open_export_gcode_dialog(self):
        # Open Export G Code dialog.
        # TODO: Pass in initial values for the dialog.
        dialog = ExportGCodeDialog(self)

        # Retrieve settings from dialog.
        export_settings = dialog.get_settings()

        # Export G code if settings are not empty.
        if export_settings:
            # Initialize instance of G code post processor.
            post_processor = GCodePostProcessor()

            # Add title comment (if specified).
            if export_settings['title_comment']['include']:
                post_processor.add_comment(export_settings['title_comment']['text'], apply_formatting=False)
                post_processor.add_linebreak()

            # Add start sequence (if specified).
            if export_settings['start_sequence']['include']:
                post_processor.add_comment(export_settings['start_sequence']['text'], apply_formatting=False)
                post_processor.add_linebreak()

            # Calculate origin offset.
            offset = self.compute_origin_offset(self.origin_position, self.workspace_dims)

            # Add circles (if specified).
            if self.circles:
                for circle in self.circles:
                    post_processor.parse_circle(circle_data=circle)
                    post_processor.add_linebreak()

            # Add roulette (if specified).
            if self.roulette:
                post_processor.parse_roulette(roulette_data=self.roulette,
                                              toolpath_data=export_settings['toolpath_parameters'],
                                              origin_offset=offset)
                post_processor.add_linebreak()

            # Add end sequence (if specified).
            if export_settings['end_sequence']['include']:
                safe_z = export_settings['toolpath_parameters']['safe_z']
                end_sequence_unformatted = export_settings['end_sequence']['text']
                end_sequence_formatted = end_sequence_unformatted.replace("<safe_Z>", f"{safe_z}")
                post_processor.add_comment(end_sequence_formatted, apply_formatting=False)

            # Save G code to file.
            post_processor.save_to_file(export_settings['file_path'])

    def compute_origin_offset(self, origin_position, workspace_dims):
        width, height = workspace_dims
        offsets = {
            (0, 0): (width / 2.0, -height / 2.0),   # top-left
            (0, 1): (0, -height / 2.0),             # top-middle
            (0, 2): (-width / 2.0, -height / 2.0),  # top-right
            (1, 0): (width / 2.0, 0),               # center-left
            (1, 1): (0, 0),                         # center
            (1, 2): (-width / 2.0, 0),              # center-right
            (2, 0): (width / 2.0, height / 2.0),    # bottom-left
            (2, 1): (0, height / 2.0),              # bottom-middle
            (2, 2): (-width / 2.0, height / 2.0),   # bottom-right
        }
        return offsets[origin_position]

    def open_settings_dialog(self):
        # Pass in initial values for the dialog
        dialog = SettingsDialog(self,
                                initial_color=self.canvas.bg_color,
                                show_origin=self.canvas.show_origin,
                                origin_position=self.canvas.origin_position
                                )
        settings = dialog.get_settings()
        self.origin_position = settings['origin_position']
        self.canvas.set_bg_color(settings['bg_color'])
        self.canvas.show_origin = settings['show_origin']
        self.canvas.origin_position = settings['origin_position']
        self.canvas.refresh_pattern()
        self.status_bar.origin_position = settings['origin_position']

    def open_info_dialog(self):
        text_list = [
            "A Celebration of Love and Friendship",  # heading
            ("This application was created in the spring of 2025 to engrave party favors "
             "for the wedding of A. Brindle and N. Saxena.")
            ]
        InfoDialog(self, text_list)

    def handle_background_color_event(self, event):
        """
        Set the background color of the workspace in response to a
        <<BackgroundColorAction>> event triggered by the workspace color picker.
        """
        # Access the data attached to the event
        self.canvas.set_bg_color(event.widget.current_color)
        self.canvas.refresh_pattern()

    def handle_pattern_lw_event(self, event):
        """
        Redraw the pattern on the canvas in response to a <<PatternLinewidthAction>>
        event triggered by the pattern linewidth spinbox. Use the new linewidth.
        """
        self.canvas.set_pattern_linewidth(int(event.widget.pattern_linewidth))
        self.canvas.refresh_pattern()

    def handle_update_circle_event(self, event):
        """
        Redraw the pattern on the canvas in response to a <<UpdateCircleAction>>
        event triggered by the widgets on the Circle Settings tab.
        """
        self.circles = event.widget.get_ring_data()
        self.canvas.set_pattern(self.circles)
        self.canvas.refresh_pattern()

    def handle_update_roulette_event(self, event):
        """
        Redraw the pattern on the canvas in response to a <<UpdateRouletteAction>>
        event triggered by the widgets on the Roulette Settings tab.
        """
        self.roulette = event.widget.get_roulette_data()
        self.canvas.set_pattern([self.roulette])  # must be a list
        self.canvas.refresh_pattern()


def center_window(window):
    """
    Center a tkinter window on the screen.

    Arguments:
        window (tk.Tk): The tkinter window to center.

    Returns:
        None
    """
    # Get most up-to-date attribute info
    window.update_idletasks()

    # Get the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the position to center the window
    size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
    x = screen_width / 2 - size[0] / 2
    y = screen_height / 2 - size[1] / 2

    # Set the geometry of the window
    window.geometry("+%d+%d" % (x, y))


# Main execution
if __name__ == "__main__":
    # Set up tkinter window
    app = SpiroScribeApp()

    # Center the window on the screen
    center_window(app)

    # Run the tkinter main loop
    app.mainloop()
