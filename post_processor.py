import numpy as np
import math
from fractions import Fraction


class GCodePostProcessor:
    def __init__(self, safe_Z_height=0.25):
        self.gcode = []  # Stores generated G-Code lines
        self.safe_Z_height = safe_Z_height

    def add_comment(self, comment, apply_formatting=True):
        """
        Add a comment to the G-Code.

        Arguments:
            comment (str): String containing the comment to add to the G-code file.

        Returns:
            None
        """
        if apply_formatting:
            self.gcode.append(f"({comment})")
        else:
            self.gcode.append(f"{comment}")

    def add_linebreak(self):
        """
        Add a blank line to the G-Code. (Useful for creating breaks between code sections.)

        Arguments:
            None

        Returns:
            None
        """
        self.gcode.append("")  # already includes newline

    def move_linear(self, x=None, y=None, z=None, feedrate=None, comment=None):
        """
        Add a linear movement command (G01).

        Arguments:
            x, y, z (float, optional): Target coordinates (ending position) for the move.
            feedrate (float, optional): Feedrate for the move.
            comment (str, optional): In-line description for the move (to be added after the command).

        Returns:
            None
        """
        command = "G01"

        # print(f'x: {x}')
        # print(f'y: {y}')
        # print(f'z: {z}')
        # print(f'feedrate: {feedrate}')
        # print(f'comment: {comment}')

        # Add command components if specified
        if x is not None:
            command += f" X{x:.3f}"
        if y is not None:
            command += f" Y{y:.3f}"
        if z is not None:
            command += f" Z{z:.3f}"
        if feedrate is not None:
            command += f" F{feedrate:.3f}"
        if comment is not None:
            command += f" ({comment})"

        # Append the generated command to the G-Code list
        self.gcode.append(command)

    def move_arc(self, x=None, y=None, i=None, j=None, clockwise=True, feedrate=None, comment=None):
        """
        Add an arc movement command (G02/G03). Arc starts at the current position.

        Rules:
            - For an arc less than 360 degrees: One or more axis words (X, Y) and one or more offsets (I, J) must be
              provided.
            - For a full circle: No axis words (X, Y) and one or more offsets (I, J) must be provided.

        Arguments:
            x, y (float, optional): Target coordinates (ending position) for the move.
            i, j (float, optional): X and Y offsets from the arc start point (current position) to the arc center point.
            clockwise (bool): Direction for the move. True for clockwise (G02), False for counterclockwise (G03).
            feedrate (float, optional): Feedrate for the move.
            comment (str, optional): In-line description for the move (to be added after the command).

        Returns:
            None
        """
        # Validate input according to the rules
        if (x is None and y is None) and (i is None or j is None):
            raise ValueError("For a full circle, at least one of I or J must be specified.")
        if (x is not None or y is not None) and (i is None and j is None):
            raise ValueError("For an arc less than 360 degrees, at least one of I or J must be specified.")

        # Determine G-Code command (G02 for clockwise, G03 for counterclockwise)
        command = "G02" if clockwise else "G03"

        # Add command components if specified
        if x is not None:
            command += f" X{x:.3f}"
        if y is not None:
            command += f" Y{y:.3f}"
        if i is not None:
            command += f" I{i:.3f}"
        if j is not None:
            command += f" J{j:.3f}"
        if feedrate is not None:
            command += f" F{feedrate:.3f}"
        if comment is not None:
            command += f" ({comment})"

        # Append the generated command to the G-Code list
        self.gcode.append(command)

    def parse_circle(self, circle_data, toolpath_data):
        """
        Parse a circle dictionary into a series of G-code moves.

        Produces:
            - Linear move 1: Rapid XY move to the left edge of the provided circle.
            - Linear move 2: Plunge Z to the provided working height.
            - Arc move: Trace a full circle in the clockwise direction at the working height.
            - Linear move 3: Rapid Z move to safe Z height.

        Arguments:
            circle_data (dict): Circle data with keys 'type', 'x', 'y', and 'radius'.
            toolpath_data (dict): TODO -- Add description here

        Returns:
            None
        """

        # Ensure the input is a circle
        if circle_data.get("type") != "circle":
            raise ValueError("The input data is not a circle.")

        # Extract parameters
        center_x = circle_data["x"]
        center_y = circle_data["y"]
        radius = circle_data["radius"]

        # Calculate starting/ending point (left edge of the circle)
        start_x = center_x - radius
        start_y = center_y

        # Calculate center offsets relative to the starting point
        i_offset = radius  # radius units to the right of starting point
        j_offset = 0.0  # vertically aligned with starting point

        # Add a comment for the circle
        self.add_comment(f"Circle at ({center_x}, {center_y}) with radius {radius}")

        # Generate G-Code commands
        self.move_linear(x=start_x, y=start_y, z=None)
        self.move_linear(x=None, y=None, z=working_height)
        self.move_arc(x=None, y=None, i=i_offset, j=j_offset, clockwise=True)
        self.move_linear(x=None, y=None, z=self.safe_Z_height)

    def parse_roulette(self, roulette_data, toolpath_data):
        """
        Parse a roulette dictionary into a series of G-code moves.

        Produces:
            - TODO: Add step 1
            - TODO: Add step 2
            - ...

        Arguments:
            roulette_data (dict): Roulette data with keys 'type', 'R', 'r', 's', 'd', and 'display res'.
            toolpath_data (dict): TODO -- Add description here

        Returns:
            None
        """

        def compute_point(theta):
            """Helper function to compute the (x, y) point for a given theta."""
            factor = (R + s * r)
            x = factor * np.cos(theta) - s * d * np.cos(theta * factor / r)
            y = factor * np.sin(theta) - d * np.sin(theta * factor / r)
            return x, y

        # Ensure the input is a roulette
        if roulette_data.get("type") != "roulette":
            raise ValueError("The input data is not a roulette.")

        # Extract roulette parameters
        R = roulette_data["R"]
        r = roulette_data["r"]
        s = roulette_data["s"]
        d = roulette_data["d"]

        # Extract toolpath parameters
        safe_z = toolpath_data['safe_z']
        jog_feed_xyz = toolpath_data['jog_feed_xyz']
        cut_feed_xy = toolpath_data['cut_feed_xy']
        cut_feed_z = toolpath_data['cut_feed_z']
        depth_per_pass = toolpath_data['depth_per_pass']
        num_passes = toolpath_data['num_passes']
        cut_res = toolpath_data['cut_res']

        # Add a comment for the roulette
        self.add_comment(f"Roulette with parameters: R={R}, r={r}, s={s}, d={d}, res={cut_res}")

        # Define R and r as fractions
        R = Fraction(R)
        r = Fraction(r)

        # Compute the effective radius
        effective_R = R + s * r

        # Compute the GCD of the numerators and denominators
        numerator_gcd = math.gcd(r.numerator, effective_R.numerator)
        denominator_lcm = (r.denominator * effective_R.denominator) // math.gcd(r.denominator, effective_R.denominator)

        # Simplify the GCD as a fraction
        gcd_fraction = Fraction(numerator_gcd, denominator_lcm)

        # Calculate the number of turns needed to close the path.
        n_turns = r / gcd_fraction
        total_angle = n_turns * 2 * np.pi
        thetas = np.linspace(0, total_angle, cut_res, endpoint=False)

        for p in range(1, num_passes + 1):
            # Compute the starting point.
            first_x, first_y = compute_point(thetas[0])
            start_x, start_y = first_x, first_y

            # Add a comment for the circle
            self.add_comment(f"====== Cut Pass {p} ======")

            # Jog to starting XY at safe Z height.
            self.move_linear(z=safe_z, feedrate=jog_feed_xyz, comment="rapid move to safe Z")
            self.move_linear(x=start_x, y=start_y, feedrate=jog_feed_xyz, comment="rapid move to XY start")

            # Plunge into material.
            self.move_linear(z=-p*depth_per_pass, feedrate=cut_feed_z, comment="Z plunge")

            # Draw the pattern by moving between consecutive points.
            for theta in thetas[1:]:
                next_x, next_y = compute_point(theta)
                self.move_linear(x=next_x, y=next_y, feedrate=cut_feed_xy)

            # Close the pattern by moving back to the starting point.
            self.move_linear(x=start_x, y=start_y, feedrate=cut_feed_xy)

    def add_start_seq(self):
        """
        Add a standardized starting sequence to the program.

        Arguments:
            None

        Returns:
            None
        """
        self.gcode.append("(Start Sequence)")
        self.gcode.append("G90 (use absolute distance mode)")
        self.gcode.append("G20 (use inch length units)")
        self.gcode.append("G94 (feed in units per minute)")
        self.gcode.append("G80 (cancel any active canned cycle)")
        self.gcode.append("G40 (cancel cutter radius compensation)")
        self.gcode.append("G49 (cancel tool length compensation)")
        self.gcode.append("G17 (set current plane to XY)")
        self.gcode.append("")

    def add_end_seq(self):
        """
        Add a standardized ending sequence to the program.

        Arguments:
            None

        Returns:
            None
        """
        self.gcode.append("")
        self.gcode.append("(End Sequence)")
        self.gcode.append(f"G00 Z{self.safe_Z_height} (rapid move to safe height)")
        self.gcode.append("G00 X0.000 Y0.000 (rapid move to origin)")
        self.gcode.append("M02 (end program)")

    def get_gcode(self):
        """
        Return the generated G-Code as a string.

        Arguments:
            None

        Returns:
            String containing all the generated G-code.
        """
        return "\n".join(self.gcode)

    def save_to_file(self, filename):
        """
        Save the generated G-Code to a file.

        Arguments:
            filename (str): The name of the destination file.

        Returns:
            None
        """

        # Ensure the filename has a .nc file extension.
        if not filename.endswith(".nc"):
            filename += ".nc"

        # Write the G-Code to the file.
        with open(filename, "w") as file:
            file.write(self.get_gcode())

        print(f"G-Code saved to {filename}")


# Example usage
if __name__ == "__main__":
    post_processor = GCodePostProcessor()
    post_processor.add_start_seq()
    post_processor.add_comment('Main Sequence')
    post_processor.move_linear(x=10, y=20, z=5, feedrate=1500)
    post_processor.move_arc(x=15, y=25, i=2.5, j=2.5, clockwise=True, feedrate=1200)
    post_processor.move_linear(x=0, y=0, z=0, feedrate=1000)
    post_processor.add_end_seq()

    # Save the G-Code to a file
    post_processor.save_to_file("output.nc")
