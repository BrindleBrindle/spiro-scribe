import numpy as np
import math
from fractions import Fraction


class SVGPostProcessor:
    def __init__(self, svg_data={}):
        """
        Converter to translate Circle and Roulette patterns into vector graphics (SVG format).

        Args:
            svg_data (dict): Dictionary of SVG document parameters.
                                  example_data = {"doc_width": 500,
                                                  "doc_height": 500,
                                                  "doc_units": "mm",
                                                  "stroke_color": "black",
                                                  "stroke_width": 1,
                                                  "pattern_fill": "none",
                                                  "include_data": True,
                                                  "display_res": 200}
        """
        # Extract settings from dictionary. Use default values if keys are missing.
        defaults = {"doc_width": 500,
                    "doc_height": 500,
                    "doc_units": "mm",
                    "stroke_color": "black",
                    "stroke_width": 2,
                    "pattern_fill": "none",
                    "include_data": False,
                    "display_res": 200}
        for key, default in defaults.items():
            setattr(self, key, svg_data.get(key, default))

        # Create a list to store SVG drawing elements.
        self.elements = []

    def parse_circle_array(self, circles):
        """
        Parse multiple circles at once into SVG <circle> elements.
        Add them to the list of drawing elements.

        Args:
            circles (list): List of circles (in dictionary form) to add to the SVG document.
                            example_data = [{"type": "circle", "x": 6.5, "y": 2.5, "radius": 1},
                                            {"type": "circle", "x": 3.5, "y": 4, "radius": 3}]
        """
        for circle in circles:
            try:
                self.parse_circle(circle)
            except Exception:
                print("Error in parsing circle array.")

    def parse_circle(self, circle_data):
        """
        Parse a circle dictionary into a corresponding SVG <circle> element.
        Add it to the list of drawing elements.

        Args:
            circle_data (dict): Dictionary of circle parameters (defined in mm).
                                example_data = {"type": "circle", "x": 6.5, "y": 2.5, "radius": 1}
        """
        # Check for missing dictionary keys.
        required_keys = ["type", "x", "y", "radius"]
        missing_keys = [key for key in required_keys if key not in circle_data]
        if missing_keys:
            raise Exception(f"Missing required keys: {', '.join(missing_keys)}")

        # Create SVG element and add it to the element list.
        if circle_data.get("type") == "circle":
            circle = SVGCircle(r=circle_data["radius"],
                               cx=circle_data["x"],
                               cy=circle_data["y"],
                               stroke_color=self.stroke_color,
                               stroke_width=self.stroke_width,
                               fill=self.pattern_fill)
            self.elements.append(circle)
        else:
            raise ValueError("The input data is not a circle.")

    def parse_roulette(self, roulette_data):
        """
        Parse a roulette dictionary into a corresponding SVG <path> element.
        Add it to the list of drawing elements.

        Args:
            roulette_data (dict): Dictionary of roulette parameters (defined in mm).
                                  example_data = {"type": "roulette", "R": 6.5, "r": 2.5, "s": 1, "d": 3.5}
        """
        def compute_point(theta):
            """Helper function to compute the (x, y) point for a given theta."""
            factor = (R + s * r)
            x = factor * np.cos(theta) - s * d * np.cos(theta * factor / r)
            y = factor * np.sin(theta) - d * np.sin(theta * factor / r)
            return x, y

        def lcm(a, b):
            """Helper function to compute the least common multiple of two numbers."""
            return (a * b) // math.gcd(a, b)

        # Check for missing dictionary keys.
        required_keys = ["type", "R", "r", "s", "d"]
        missing_keys = [key for key in required_keys if key not in roulette_data]
        if missing_keys:
            raise Exception(f"Missing required keys: {', '.join(missing_keys)}")

        # Create SVG element and add it to the element list.
        if roulette_data.get("type") == "roulette":
            # Extract roulette parameters.
            R = Fraction(roulette_data["R"])  # define as fraction
            r = Fraction(roulette_data["r"])  # define as fraction
            s = roulette_data["s"]
            d = roulette_data["d"]
            display_res = self.display_res

            # Compute the effective radius.
            effective_R = R + s * r

            # Compute the GCD of the numerators and the LCM of the denominators.
            numerator_gcd = math.gcd(r.numerator, effective_R.numerator)
            denominator_lcm = lcm(r.denominator, effective_R.denominator)

            # Simplify as a fraction.
            gcd_fraction = Fraction(numerator_gcd, denominator_lcm)

            # Calculate the number of turns needed to close the path.
            n_turns = r / gcd_fraction
            total_angle = n_turns * 2 * np.pi
            thetas = np.linspace(0, total_angle, display_res, endpoint=False)

            # Create a new path element and move to the starting point.
            path = SVGPath(stroke_color=self.stroke_color, stroke_width=self.stroke_width, fill=self.pattern_fill)
            start_x, start_y = compute_point(thetas[0])
            path.move_to(start_x, start_y)

            # Make line segments between successive XY locations.
            for theta in thetas[1:]:
                next_x, next_y = compute_point(theta)
                path.line_to(next_x, next_y)

            # Close the pattern by moving back to the start.
            path.close_path()

            # Add the finished path to the list of drawing elements. 
            self.elements.append(path)

        else:
            raise ValueError("The input data is not a roulette.")

    def save(self, filename):
        """
        Generate the SVG string for the entire document and save it to a file.
        
        Args:
            filename (str): Name of the file to save the SVG.
        """
        with open(filename, "w") as file:
            elements_svg = "\n".join([element.to_svg() for element in self.elements])
            background_svg = '<rect width="100%" height="100%" fill="peachpuff"/>'
            doc_string = (f'<svg width="{self.doc_width}{self.doc_units}" height="{self.doc_height}{self.doc_units}" '
                          f'xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
                          f'{background_svg}\n'
                          f'{elements_svg}\n</svg>')
            file.write(doc_string)


class SVGTextBox:
    """
    Displays data about an SVG drawing element.
    """
    def __init__(self):
        pass

    def to_svg(self):
        pass


class SVGCircle:
    """
    Represents an SVG <circle> element.
    """
    def __init__(self, r, cx=0, cy=0, units="mm", stroke_color="black", stroke_width=1, fill="none"):
        """
        Initialize a circle element with optional stroke, fill, and stroke width.
        
        Args:
            r (float): Radius of the circle.
            cx (float): X-axis center of the circle (default: 0).
            cy (float): Y-axis center of the circle (default: 0).
            units (str): Units, either "mm" or "in" (default: "mm").
            stroke_color (str): Stroke color of the circle (default: "black").
            stroke_width (int): Stroke width of the circle (default: 1).
            fill (str): Fill color of the circle (default: "none").
        """
        self.r = r
        self.cx = cx
        self.cy = cy
        self.units = units
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
            f'<circle\n\tr="{self.r}{self.units}"\n\tcx="{self.cx}{self.units}"\n\tcy="{self.cy}{self.units}"'
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


# Example usage
if __name__ == "__main__":
    # Example SVG data.
    svg_data = {"doc_width": 100, "doc_height": 100, "doc_units": "mm", "stroke_color": "slategray"}

    # Create an instance of the post processor.
    post_processor = SVGPostProcessor(svg_data)

    # Create example patterns.
    example_circle = {"type": "circle", "x": 50, "y": 50, "radius": 10}
    # example_roulette = {"type": "roulette", "R": 6.5, "r": 2.5, "s": 1, "d": 3.5}

    # Parse the patterns.
    post_processor.parse_circle(example_circle)
    # post_processor.parse_roulette(example_roulette)

    # Save the SVG document.
    post_processor.save("svg_with_example_patterns.svg")

    print("SVG file 'svg_with_example_patterns.svg' has been created!")
