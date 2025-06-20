import numpy as np
import math
from fractions import Fraction


class SVGPostProcessor:
    def __init__(self, svg_data={}):
        """
        Converter to translate circle and roulette patterns into vector graphics (SVG format).

        Args:
            svg_data (dict): Dictionary of SVG document parameters.
                                  example_data = {"svg_width": 400,
                                                  "svg_height": 400,
                                                  "workspace_width": 32,
                                                  "workspace_height": 32,
                                                  "workspace_units": 'mm',
                                                  "stroke_color": "black",
                                                  "stroke_width": 1,
                                                  "include_params": True,
                                                  "path_resolution": 200}
        """
        # Extract settings from dictionary. Use default values if keys are missing.
        defaults = {"svg_width": 400,
                    "svg_height": 400,
                    "workspace_width": 32,
                    "workspace_height": 32,
                    "workspace_units": 'mm',
                    "stroke_color": "black",
                    "stroke_width": 0.5,
                    "include_params": True,
                    "path_resolution": 1000}
        for key, default in defaults.items():
            setattr(self, key, svg_data.get(key, default))

        # Create variables to store generated SVG drawing elements.
        self.pattern_svg = ''
        self.parameters_svg = ''

    def parse_pattern(self, pattern):
        """
        TODO: Add a function description here.

        Args:
            TODO: Add an argument description here.
        """
        if pattern['type'] == 'roulette':
            self.parse_roulette(pattern)
        elif pattern['type'] == 'circle array':
            self.parse_circle_array(pattern)
        else:
            raise ValueError('Pattern must be a valid roulette or circle array dictionary.')

    def parse_circle_array(self, circle_data):
        """
        Parse a circle array dictionary into SVG <path> and <text> elements.

        Args:
            circle_data (dict): Dictionary of circle array parameters (defined in mm).
                                example_data = {"type": "circle array", "D": 6.5, "d": 2.5, "n": 6}
                                example_data = {"type": "circle array", "D": [4.0, 11.0], "d": [5.5, 1.0], "n": [7, 20]}
        """
        self.pattern_svg = ''
        self.parameters_svg = ''

        # Extract circle array parameters.
        ring_diameters = circle_data["D"]
        circle_diameters = circle_data["d"]
        num_circles = circle_data["n"]

        text_pos = self.workspace_height + 2.0

        for i in range(0, len(ring_diameters)):
            angles = np.linspace(0, 2 * np.pi, num_circles[i], endpoint=False)
            for theta in angles:
                r = circle_diameters[i] / 2.0
                cx = (ring_diameters[i] / 2.0) * np.cos(theta)
                cy = (ring_diameters[i] / 2.0) * np.sin(theta)
                cx_offset = cx + self.workspace_width / 2.0  # offset to middle of canvas
                cy_offset = cy + self.workspace_width / 2.0  # offset to middle of canvas
                self.pattern_svg += (f'\t<circle\n\t\tr="{r}"\n\t\tcx="{cx_offset}"\n\t\tcy="{cy_offset}"'
                                     f'\n\t\tstroke="{self.stroke_color}"\n\t\tstroke-width="{self.stroke_width}"\n\t\tfill="none" />\n')

            parameters = [('Ring Diameter (D):', f'{float(ring_diameters[i])}{self.workspace_units}'),
                          ('Circle Diameter (d):', f'{float(circle_diameters[i])}{self.workspace_units}'),
                          ('# Circles:', num_circles[i])]

            self.parameters_svg += (f'\t<text x="1" y="{text_pos}" font-size="1.25" font-weight="bold">Circle Array {i + 1}</text>\n')
            text_pos += 1.75  # advance text position by 1.75 units

            for j in range(0, len(parameters)):
                self.parameters_svg += (f'\t<text x="1" y="{text_pos}" font-size="1.25">\n'
                                        f'\t\t<tspan>{parameters[j][0]}</tspan>\n'
                                        f'\t\t<tspan x="15">{parameters[j][1]}</tspan>\n'
                                        f'\t</text>\n')
                text_pos += 1.75  # advance text position by 1.75 units

            text_pos += 0.75

    def parse_roulette(self, roulette_data):
        """
        Parse a roulette dictionary into SVG <path> and <text> elements.

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

        # Extract roulette parameters.
        R = Fraction(roulette_data["R"])  # define as fraction
        r = Fraction(roulette_data["r"])  # define as fraction
        s = roulette_data["s"]
        d = roulette_data["d"]

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
        thetas = np.linspace(0, total_angle, self.path_resolution, endpoint=False)

        # Create a new path command string and move to the starting point.
        path_commands = ""
        start_x, start_y = compute_point(thetas[0])
        start_x_offset = start_x + self.workspace_width / 2.0  # offset to middle of canvas
        start_y_offset = start_y + self.workspace_height / 2.0  # offset to middle of canvas
        path_commands += f"\t\t\tM {start_x_offset} {start_y_offset}\n"  # move to (absolute)

        # Make line segments between successive XY locations.
        for theta in thetas[1:]:
            next_x, next_y = compute_point(theta)
            next_x_offset = next_x + self.workspace_width / 2.0  # offset to middle of canvas
            next_y_offset = next_y + self.workspace_height / 2.0  # offset to middle of canvas
            path_commands += f"\t\t\tL {next_x_offset} {next_y_offset}\n"  # line to (absolute)

        # Close the pattern by moving back to the start.
        path_commands += "\t\t\tZ\n"

        # Set the pattern and parameter attributes.
        self.pattern_svg = (f'\t<path\n\t\td="{path_commands.strip()}"\n\t\tstroke="{self.stroke_color}"'
                            f'\n\t\tstroke-width="{self.stroke_width}"\n\t\tfill="none" />\n')

        parameters = [('Fixed Circle Radius (R):', f'{float(R)}{self.workspace_units}'),
                      ('Rolling Circle Radius (r):', f'{float(r)}{self.workspace_units}'),
                      ('Rolling Side (s):', 'Inside' if s == -1 else 'Outside'),
                      ('Pen Distance (d):', f'{float(d)}{self.workspace_units}')]

        text_pos = self.workspace_height + 2.0
        self.parameters_svg = (f'\t<text x="1" y="{text_pos}" font-size="1.25" font-weight="bold">Roulette</text>\n')
        text_pos += 1.75  # advance text position by 1.75 units
        for i in range(0, len(parameters)):
            self.parameters_svg += (f'\t<text x="1" y="{text_pos}" font-size="1.25">\n'
                                    f'\t\t<tspan>{parameters[i][0]}</tspan>\n'
                                    f'\t\t<tspan x="15">{parameters[i][1]}</tspan>\n'
                                    f'\t</text>\n')
            text_pos += 1.75  # advance text position by 1.75 units

    def save(self, filename):
        """
        Generate the SVG string for the entire document and save it to a file.
        
        Args:
            filename (str): Name of the file to be created.
        """
        with open(filename, "w") as file:
            if self.include_params:
                height = self.svg_height + 300
                viewbox_height = self.workspace_height + 24
                parameters_svg = (f'\n\t<!-- Parameters -->\n'
                                  f'{self.parameters_svg}')
            else:
                height = self.svg_height
                viewbox_height = self.workspace_height
                parameters_svg = ''

            doc_string = (f'<svg width="{self.svg_width}" height="{height}" viewBox="0 0 {self.workspace_width} {viewbox_height}" xmlns="http://www.w3.org/2000/svg" version="1.1">\n\n'
                          f'\t<!-- Background -->\n'
                          f'\t<rect x="0" y="0" width="{self.workspace_width}" height="{self.workspace_height}" fill="whitesmoke"/>\n\n'
                          f'\t<!-- Pattern -->\n'
                          f'{self.pattern_svg}'
                          f'{parameters_svg}'
                          f'\n</svg>')

            file.write(doc_string)


# Example usage
if __name__ == "__main__":
    # Create an instance of the post processor.
    example_settings = {"svg_width": 400, "svg_height": 400,
                        "workspace_width": 32, "workspace_height": 32, "workspace_units": 'mm',
                        "stroke_width": 0.25, "stroke_color": "slategray", "include_params": True}
    post_processor = SVGPostProcessor(example_settings)

    # Parse an example pattern and save it to a file.
    # example_pattern = {"type": "roulette", "R": 5.5, "r": 2.5, "s": 1, "d": 3.5}
    example_pattern = {"type": "circle array", "D": [4.0, 11.0, 0], "d": [5.5, 1.0, 12.5], "n": [7, 20, 1]}
    post_processor.parse_pattern(example_pattern)
    post_processor.save("svg_with_example_patterns.svg")

    print("SVG file 'svg_with_example_patterns.svg' has been created!")
