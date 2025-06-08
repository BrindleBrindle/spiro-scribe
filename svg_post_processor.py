class SVGPostProcessor:
    """
    Converts provided Circle and Roulette patterns into vector graphics (SVG format).
    """
    def __init__(self):
        # Create an SVG document
        self.doc = SVGDocument(500, 500)  # SVG document
        self.elements = []  # list of drawing elements

    def parse_circle_array(self):
        # TODO: Fill in code here.
        pass

    def parse_circle(self, circle_data, svg_data):
        """
        Parse a circle dictionary into a corresponding SVG <path> element.

        Arguments:
            circle_data (dict): Dictionary of circle parameters (defined in mm).
                                  example_data = {"type": "circle",
                                                  "x": 6.5,
                                                  "y": 2.5,
                                                  "radius": 1}
            svg_data (dict): Dictionary of SVG output parameters. TODO: Show example data here.

        Returns:
            None
        """

        # Ensure the input is a circle
        if circle_data.get("type") != "circle":
            raise ValueError("The input data is not a circle.")

        # Extract circle parameters (defined in mm).
        center_x = circle_data["x"]
        center_y = circle_data["y"]
        radius = circle_data["radius"]

        # TODO: Extract SVG parameters.
        # Add SVG parameters:
        #   - stroke_color
        #   - stroke_width
        #   - fill

        circle = SVGCircle(r=radius, cx=center_x, cy=center_y, stroke_color="black", stroke_width=1, fill="none")
        self.doc.add_element(circle)

    # def parse_roulette(self, roulette_data, toolpath_data, origin_offset):
    #     """
    #     Parse a roulette dictionary into a series of G code commands.
    #     Append the commands to the local G code program.

    #     Produces:
    #         1) Comment containing roulette parameters.
    #         2) Comment containing cut pass number.
    #         3) G01: Rapid Z to safe Z height.
    #         4) G01: Rapid XY to XY start.
    #         5) G01: Z plunge to cutting depth at Z feedrate.
    #         6) G01: Move to successive XY points at XY feedrate until pattern is complete.
    #         Repeat steps (2)-(6) for specified number of passes.

    #     Arguments:
    #         roulette_data (dict): Dictionary of roulette parameters (defined in mm).
    #                               example_data = {"type": "roulette",
    #                                               "R": 6.5,
    #                                               "r": 2.5,
    #                                               "s": 1,
    #                                               "d": 3.5,
    #                                               "display_res": 200}
    #         toolpath_data (dict): Dictionary of machining parameters (defined in mm or in).
    #                               example_data = {"units": "imperial",
    #                                               "safe_z": 0.25,
    #                                               "jog_feed_xyz": 8.0,
    #                                               "cut_feed_xy": 2.0,
    #                                               "cut_feed_z": 1.0,
    #                                               "depth_per_pass": 0.02,
    #                                               "num_passes": 1,
    #                                               "cut_res": 200}
    #         origin_offset (tuple): X and Y amounts (defined in mm) by which to translate
    #                                pattern to account for origin location (dX, dY).

    #     Returns:
    #         None
    #     """

    #     def compute_point(theta):
    #         """Helper function to compute the (x, y) point for a given theta."""
    #         factor = (R + s * r)
    #         x = factor * np.cos(theta) - s * d * np.cos(theta * factor / r)
    #         y = factor * np.sin(theta) - d * np.sin(theta * factor / r)
    #         return x, y

    #     # Ensure the input is a roulette
    #     if roulette_data.get("type") != "roulette":
    #         raise ValueError("The input data is not a roulette.")

    #     # Extract units.
    #     units = toolpath_data['units']

    #     # Extract roulette parameters (defined in mm). Convert to inches if units not metric.
    #     if units == "metric":
    #         R = roulette_data["R"]
    #         r = roulette_data["r"]
    #         s = roulette_data["s"]
    #         d = roulette_data["d"]
    #     else:
    #         R = roulette_data["R"] / 25.4
    #         r = roulette_data["r"] / 25.4
    #         s = roulette_data["s"]
    #         d = roulette_data["d"] / 25.4

    #     # Extract toolpath parameters (already in correct units).
    #     safe_z = toolpath_data['safe_z']
    #     jog_feed_xyz = toolpath_data['jog_feed_xyz']
    #     cut_feed_xy = toolpath_data['cut_feed_xy']
    #     cut_feed_z = toolpath_data['cut_feed_z']
    #     depth_per_pass = toolpath_data['depth_per_pass']
    #     num_passes = toolpath_data['num_passes']
    #     cut_res = toolpath_data['cut_res']

    #     # Extract origin offsets (defined in mm).
    #     if units == "metric":
    #         offset_x, offset_y = origin_offset
    #     else:
    #         offset_x = origin_offset(0) / 25.4
    #         offset_y = origin_offset(1) / 25.4

    #     # Add a comment for the roulette.
    #     self.add_comment(f"Roulette with parameters: R={R}, r={r}, s={s}, d={d}, res={cut_res}")

    #     # Define R and r as fractions.
    #     R = Fraction(R)
    #     r = Fraction(r)

    #     # Compute the effective radius.
    #     effective_R = R + s * r

    #     # Compute the GCD of the numerators and denominators.
    #     numerator_gcd = math.gcd(r.numerator, effective_R.numerator)
    #     denominator_lcm = (r.denominator * effective_R.denominator) // math.gcd(r.denominator, effective_R.denominator)

    #     # Simplify the GCD as a fraction.
    #     gcd_fraction = Fraction(numerator_gcd, denominator_lcm)

    #     # Calculate the number of turns needed to close the path.
    #     n_turns = r / gcd_fraction
    #     total_angle = n_turns * 2 * np.pi
    #     thetas = np.linspace(0, total_angle, cut_res, endpoint=False)

    #     for p in range(1, num_passes + 1):
    #         # Compute the starting point.
    #         first_x, first_y = compute_point(thetas[0])
    #         start_x, start_y = first_x, first_y
    #         start_x_offset = start_x + offset_x  # to account for origin location
    #         start_y_offset = start_y + offset_y  # to account for origin location

    #         # Add a comment with the number of the current pass.
    #         self.add_comment(f"====== Cut Pass {p} ======")

    #         # Jog to starting XY at safe Z height.
    #         self.move_linear(z=safe_z, feedrate=jog_feed_xyz, comment="rapid move to safe Z")
    #         self.move_linear(x=start_x_offset, y=start_y_offset, feedrate=jog_feed_xyz,
    #                          comment="rapid move to XY start")

    #         # Plunge into material.
    #         self.move_linear(z=-p*depth_per_pass, feedrate=cut_feed_z, comment="Z plunge")

    #         # Move to the next XY location.
    #         for theta in thetas[1:]:
    #             next_x, next_y = compute_point(theta)
    #             next_x_offset = next_x + offset_x
    #             next_y_offset = next_y + offset_y
    #             self.move_linear(x=next_x_offset, y=next_y_offset, feedrate=cut_feed_xy)

    #         # Close the pattern by moving back to the starting point.
    #         self.move_linear(x=start_x_offset, y=start_y_offset, feedrate=cut_feed_xy)


class SVGCircle:
    """
    Represents an SVG <circle> element.
    """
    def __init__(self, r, cx=0, cy=0, stroke_color="black", stroke_width=1, fill="none"):
        """
        Initialize a circle element with optional stroke, fill, and stroke width.
        
        Args:
            r (float): Radius of the circle.
            cx (float): X-axis center of the circle (default: 0).
            cy (float): Y-axis center of the circle (default: 0).
            stroke_color (str): Stroke color of the circle (default: "black").
            stroke_width (int): Stroke width of the circle (default: 1).
            fill (str): Fill color of the circle (default: "none").
        """
        self.r = r
        self.cx = cx
        self.cy = cy
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.fill = fill

    def to_svg(self):
        """
        Generate the SVG string for the circle element.
        
        Returns:
            str: The SVG representation of the circle.
        """
        return (
            f'<circle\n\tr="{self.r}"\n\tcx="{self.cx}"\n\tcy="{self.cy}"'
            f'\n\tstroke="{self.stroke_color}"\n\tstroke-width="{self.stroke_width}"'
            f'\n\tfill="{self.fill}" />'
        )


class SVGPath:
    """
    Represents an SVG <path> element that supports incremental path command construction.
    """
    def __init__(self, stroke_color="black", stroke_width=1, fill="none"):
        """
        Initialize a path element with optional stroke color, stroke width, and fill.
        
        Args:
            stroke_color (str): Stroke color of the path (default: "black").
            stroke_width (int): Stroke width of the path (default: 1).
            fill (str): Fill color of the path (default: "none").
        """
        self.d = ""  # the 'd' attribute that stores the path commands
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.fill = fill

    # Move To (M) - Absolute
    def move_to(self, x, y):
        self.d += f"\t\tM{x} {y} \n"

    # Move To (m) - Relative
    def move_by(self, dx, dy):
        self.d += f"\t\tm{dx} {dy} \n"

    # Line To (L) - Absolute
    def line_to(self, x, y):
        self.d += f"\t\tL{x} {y} \n"

    # Line To (l) - Relative
    def line_by(self, dx, dy):
        self.d += f"\t\tl{dx} {dy} \n"

    # Horizontal Line To (H) - Absolute
    def horizontal_to(self, x):
        self.d += f"\t\tH{x} \n"

    # Horizontal Line To (h) - Relative
    def horizontal_by(self, dx):
        self.d += f"\t\th{dx} \n"

    # Vertical Line To (V) - Absolute
    def vertical_to(self, y):
        self.d += f"\t\tV{y} \n"

    # Vertical Line To (v) - Relative
    def vertical_by(self, dy):
        self.d += f"\t\tv{dy} \n"

    # Close Path (Z or z)
    def close_path(self):
        self.d += "\t\tZ \n"

    def to_svg(self):
        """
        Generate the SVG string for the path element.
        
        Returns:
            str: The SVG representation of the path.
        """
        return (
            f'<path\n\td="{self.d.strip()}"\n\tstroke="{self.stroke_color}"\n\tstroke-width="{self.stroke_width}"\n'
            f'\tfill="{self.fill}" />'
        )


class SVGDocument:
    """
    Represents an SVG document.
    """
    def __init__(self, width, height):
        """
        Initialize the SVG document with dimensions.
        
        Args:
            width (int): Width of the SVG canvas.
            height (int): Height of the SVG canvas.
        """
        self.width = width
        self.height = height
        self.elements = []  # list to store drawing elements (<path> or <circle>)

    def add_element(self, e):
        """
        Add a pre-constructed SVGPath or SVGCircle object to the document.
        
        Args:
            e (SVGPath or SVGCircle): The drawing object to add.
        """
        self.paths.append(e)

    def save(self, filename):
        """
        Save the SVG document to a file.
        
        Args:
            filename (str): Name of the file to save the SVG.
        """
        with open(filename, "w") as file:
            file.write(self.to_svg())

    def to_svg(self):
        """
        Generate the SVG string for the entire document.
        
        Returns:
            str: The SVG representation of the document.
        """
        paths_svg = "\n".join([path.to_svg() for path in self.paths])
        return (
            f'<svg width="{self.width}" height="{self.height}" '
            f'xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
            f'{paths_svg}\n</svg>'
        )


# Example usage
if __name__ == "__main__":
    # Create an SVG document
    doc = SVGDocument(500, 500)

    # Create a path and incrementally add commands
    path1 = SVGPath(stroke="blue", fill="none", stroke_width=2)
    path1.move_to(10, 10)      # Absolute move to (10, 10)
    path1.line_to(100, 10)     # Absolute line to (100, 10)
    path1.vertical_to(100)     # Absolute vertical line to y=100
    path1.horizontal_to(10)    # Absolute horizontal line to x=10
    path1.close_path()         # Close the path (Z)

    # Create another path
    path2 = SVGPath(stroke="red", fill="none", stroke_width=1)
    path2.move_to(150, 150)    # Absolute move to (150, 150)
    path2.line_by(50, 0)       # Relative line by (50, 0)
    path2.vertical_by(50)      # Relative vertical line by 50
    path2.horizontal_by(-50)   # Relative horizontal line by -50
    path2.close_path()         # Close the path (z)

    # Add the paths to the document
    doc.add_element(path1)
    doc.add_element(path2)

    # Save the SVG document
    doc.save("svg_with_path_commands.svg")

    print("SVG file 'svg_with_path_commands.svg' has been created!")
