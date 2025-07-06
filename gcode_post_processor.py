import numpy as np
import math
from fractions import Fraction


class GCodePostProcessor:
    def __init__(self, units):
        self.units = units
        self.gcode = []  # stores generated G code lines

    def add_comment(self, comment, apply_formatting=True, indent_amount=0):
        """
        Add a comment to the G code.

        Args:
            comment (str): String containing the comment to add to the G code compilation.
        """
        if apply_formatting:
            self.gcode.append(indent_amount * "\t" + f"({comment})")
        else:
            self.gcode.append(f"{comment}")

    def add_linebreak(self):
        """
        Add a blank line to the G code. (Useful for creating breaks between code sections.)
        """
        self.gcode.append("")  # already includes newline

    def move_linear(self, x=None, y=None, z=None, feedrate=None, comment=None, indent_amount=0):
        """
        Add a linear move (G01 command) to the G code.

        Args:
            x, y, z (float, optional): Target coordinates (ending position) for the move.
            feedrate (float, optional): Feedrate for the move.
            comment (str, optional): In-line description for the move (to be added after the command).
        """

        # Initialize command string. Add extra components if specified.
        command = indent_amount * "\t" + "G01"
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

        # Append the generated command to the G code list
        self.gcode.append(command)

    def move_arc(self, x=None, y=None, i=None, j=None, clockwise=True, feedrate=None, comment=None, indent_amount=0):
        """
        Add an arc move (G02/G03 command) to the G code. Arc starts at the current position.

        Rules:
            - For an arc less than 360 degrees: One or more axis words (X, Y) and one or more offsets (I, J) must be
              provided.
            - For a full circle: No axis words (X, Y) and one or more offsets (I, J) must be provided.

        Args:
            x, y (float, optional): Target coordinates (ending position) for the move.
            i, j (float, optional): X and Y offsets from the arc start point (current position) to the arc center point.
            clockwise (bool): Direction for the move. True for clockwise (G02), False for counterclockwise (G03).
            feedrate (float, optional): Feedrate for the move.
            comment (str, optional): In-line description for the move (to be added after the command).
        """

        # Validate input according to the rules
        if (x is None and y is None) and (i is None or j is None):
            raise ValueError("For a full circle, at least one of I or J must be specified.")
        if (x is not None or y is not None) and (i is None and j is None):
            raise ValueError("For an arc less than 360 degrees, at least one of I or J must be specified.")

        # Determine G code command (G02 for clockwise, G03 for counterclockwise)
        command = indent_amount * "\t" + "G02" if clockwise else indent_amount * "\t" + "G03"

        # Add extra components if specified
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

        # Append the generated command to the G code list
        self.gcode.append(command)

    def parse_circle_array(self, circle_array_data, toolpath_data, origin_offset):
        """
        Parse a circle array dictionary into a series of G code commands.
        Append the commands to the local G code program.

        Produces:
            For each circle in array:
                1) Comment containing cut pass number.
                2) G01: Rapid Z to safe Z height.
                3) G01: Rapid XY to XY start.
                4) G01: Z plunge to cutting depth at Z feedrate.
                5) G02: Move to successive XY points at XY feedrate until pattern is complete.
                Repeat steps (2)-(6) for specified number of passes.

        Args:
            circle_array_data (dict): Dictionary of circle array parameters (defined in mm).
                                      example_data = {"type": "circle array",
                                                      "D": [4.0, 11.0],
                                                      "d": [5.5, 1.0],
                                                      "n": [7, 20]}
            toolpath_data (dict): Dictionary of machining parameters (defined in mm or in).
                                  example_data = {"safe_z": 0.25,
                                                  "jog_feed_xyz": 8.0,
                                                  "cut_feed_xy": 2.0,
                                                  "cut_feed_z": 1.0,
                                                  "depth_per_pass": 0.02,
                                                  "num_passes": 1,
                                                  "cut_res": 200}
            origin_offset (tuple): X and Y amounts (defined in mm) by which to translate
                                   pattern to account for origin location (dX, dY).
        """

        # Ensure the input is a circle
        if circle_array_data.get("type") != "circle array":
            raise ValueError("The input data is not a circle array.")

        # Extract circle array parameters (defined in mm). Convert to inches if units not metric.
        if self.units == "metric":
            D = circle_array_data["D"]
            d = circle_array_data["d"]
            n = circle_array_data["n"]
        else:
            D = [x / 25.4 for x in circle_array_data["D"]]
            d = [x / 25.4 for x in circle_array_data["d"]]
            n = circle_array_data["n"]

        # Extract toolpath parameters (already in the correct units).
        safe_z = float(toolpath_data['safe_z'])
        jog_feed_xyz = float(toolpath_data['jog_feed_xyz'])
        cut_feed_xy = float(toolpath_data['cut_feed_xy'])
        cut_feed_z = float(toolpath_data['cut_feed_z'])
        depth_per_pass = float(toolpath_data['depth_per_pass'])
        num_passes = int(toolpath_data['num_passes'])

        # Extract origin offsets (defined in mm). Convert to inches if units not metric.
        if self.units == "metric":
            offset_x, offset_y = origin_offset
        else:
            offset_x = origin_offset(0) / 25.4
            offset_y = origin_offset(1) / 25.4

        # Add a comment for the main program
        self.add_comment("MAIN PROGRAM - MACHINING OPERATIONS")

        # For each ring:
        for i in range(0, len(D)):

            # Add a comment with the number of the current ring.
            self.add_comment(f"------ Circle Array {i + 1} ------", indent_amount=1)
            self.add_comment(f"Parameters: D={D[i]}, d={d[i]}, n={n[i]}", indent_amount=1)
            self.add_linebreak()

            # For each circle in the circle array:
            angles = np.linspace(0, 2 * np.pi, n[i], endpoint=False)
            for j in range(0, len(angles)):

                # Add a comment with the number of the current circle.
                self.add_comment(f"------ Circle {j + 1} of {n[i]} ------", indent_amount=2)

                r = d[i] / 2.0
                cx = (D[i] / 2.0) * np.cos(j)
                cy = (D[i] / 2.0) * np.sin(j)

                # Calculate starting/ending point (left edge of the circle).
                start_x = cx - r
                start_y = cy
                start_x_offset = start_x + offset_x  # to account for origin location
                start_y_offset = start_y + offset_y  # to account for origin location

                # Calculate center offsets relative to the starting point.
                i_offset = r  # radius units to the right of starting point
                j_offset = 0.0  # vertically aligned with starting point

                # For each pass
                for p in range(1, num_passes + 1):
                    # Add a comment with the number of the current pass.
                    self.add_comment(f"Cut Pass {p} of {num_passes}", indent_amount=2)

                    # Jog to starting XY at safe Z height.
                    self.move_linear(z=safe_z, feedrate=jog_feed_xyz, comment="rapid move to safe Z", indent_amount=2)
                    self.move_linear(x=start_x_offset, y=start_y_offset, feedrate=jog_feed_xyz,
                                     comment="rapid move to XY start", indent_amount=2)

                    # Plunge into material.
                    self.move_linear(z=-p*depth_per_pass, feedrate=cut_feed_z, comment="Z plunge", indent_amount=2)

                    # Cut arc in clockwise motion.
                    self.move_arc(x=None, y=None, i=i_offset, j=j_offset, clockwise=True, feedrate=cut_feed_xy,
                                  comment="clockwise arc", indent_amount=2)

                    self.add_linebreak()

    def parse_roulette(self, roulette_data, toolpath_data, origin_offset):
        """
        Parse a roulette dictionary into a series of G code commands.
        Append the commands to the local G code program.

        Produces:
            1) Comment containing roulette parameters.
            2) Comment containing cut pass number.
            3) G01: Rapid Z to safe Z height.
            4) G01: Rapid XY to XY start.
            5) G01: Z plunge to cutting depth at Z feedrate.
            6) G01: Move to successive XY points at XY feedrate until pattern is complete.
            Repeat steps (2)-(6) for specified number of passes.

        Args:
            roulette_data (dict): Dictionary of roulette parameters (defined in mm).
                                  example_data = {"type": "roulette",
                                                  "R": 6.5,
                                                  "r": 2.5,
                                                  "s": 1,
                                                  "d": 3.5,
                                                  "display_res": 200}
            toolpath_data (dict): Dictionary of machining parameters (defined in mm or in).
                                  example_data = {"safe_z": 0.25,
                                                  "jog_feed_xyz": 8.0,
                                                  "cut_feed_xy": 2.0,
                                                  "cut_feed_z": 1.0,
                                                  "depth_per_pass": 0.02,
                                                  "num_passes": 1,
                                                  "cut_res": 200}
            origin_offset (tuple): X and Y amounts (defined in mm) by which to translate
                                   pattern to account for origin location (dX, dY).
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

        # Ensure the input is a roulette
        if roulette_data.get("type") != "roulette":
            raise ValueError("The input data is not a roulette.")

        # Extract roulette parameters (defined in mm). Convert to inches if units not metric.
        if self.units == "metric":
            R = roulette_data["R"]
            r = roulette_data["r"]
            s = roulette_data["s"]
            d = roulette_data["d"]
        else:
            R = roulette_data["R"] / 25.4
            r = roulette_data["r"] / 25.4
            s = roulette_data["s"]
            d = roulette_data["d"] / 25.4

        # Extract toolpath parameters (already in correct units).
        safe_z = float(toolpath_data['safe_z'])
        jog_feed_xyz = float(toolpath_data['jog_feed_xyz'])
        cut_feed_xy = float(toolpath_data['cut_feed_xy'])
        cut_feed_z = float(toolpath_data['cut_feed_z'])
        depth_per_pass = float(toolpath_data['depth_per_pass'])
        num_passes = int(toolpath_data['num_passes'])
        cut_res = int(toolpath_data['cut_res'])

        # Extract origin offsets (defined in mm).
        if self.units == "metric":
            offset_x, offset_y = origin_offset
        else:
            offset_x = origin_offset(0) / 25.4
            offset_y = origin_offset(1) / 25.4

        # Add a comment for the main program
        self.add_comment("MAIN PROGRAM - MACHINING OPERATIONS")

        # Add a comment for the roulette.
        self.add_comment("------ Roulette ------", indent_amount=1)
        self.add_comment(f"Parameters: R={R}, r={r}, s={s}, d={d}, res={cut_res}", indent_amount=1)
        self.add_linebreak()

        # Define R and r as fractions.
        R = Fraction(R)
        r = Fraction(r)

        # Compute the effective radius.
        effective_R = R + s * r

        # Compute the GCD of the numerators and the LCM of the denominators.
        numerator_gcd = math.gcd(r.numerator, effective_R.numerator)
        denominator_lcm = lcm(r.denominator, effective_R.denominator)

        # Simplify as a fraction.
        gcd_fraction = Fraction(numerator_gcd, denominator_lcm)

        # Simplify the GCD as a fraction.
        gcd_fraction = Fraction(numerator_gcd, denominator_lcm)

        # Calculate the number of turns needed to close the path.
        n_turns = r / gcd_fraction
        total_angle = n_turns * 2 * np.pi
        thetas = np.linspace(0, total_angle, cut_res, endpoint=False)

        for p in range(1, num_passes + 1):
            # Add a comment with the number of the current pass.
            self.add_comment(f"Cut Pass {p} of {num_passes}", indent_amount=2)

            # Compute the starting point.
            first_x, first_y = compute_point(thetas[0])
            start_x, start_y = first_x, first_y
            start_x_offset = start_x + offset_x  # to account for origin location
            start_y_offset = start_y + offset_y  # to account for origin location

            # Jog to starting XY at safe Z height.
            self.move_linear(z=safe_z, feedrate=jog_feed_xyz, comment="rapid move to safe Z", indent_amount=2)
            self.move_linear(x=start_x_offset, y=start_y_offset, feedrate=jog_feed_xyz,
                             comment="rapid move to XY start", indent_amount=2)

            # Plunge into material.
            self.move_linear(z=-p*depth_per_pass, feedrate=cut_feed_z, comment="Z plunge", indent_amount=2)

            # Move to the next XY location.
            for theta in thetas[1:]:
                next_x, next_y = compute_point(theta)
                next_x_offset = next_x + offset_x
                next_y_offset = next_y + offset_y
                self.move_linear(x=next_x_offset, y=next_y_offset, feedrate=cut_feed_xy, indent_amount=2)

            # Close the pattern by moving back to the starting point.
            self.move_linear(x=start_x_offset, y=start_y_offset, feedrate=cut_feed_xy, indent_amount=2)

            self.add_linebreak()

    def get_gcode(self):
        """
        Return the generated G code as a string.

        Returns:
            String containing all the generated G code.
        """
        return "\n".join(self.gcode)

    def clear_gcode(self):
        """
        Clear the G code in the active string.
        """
        return "\n".join(self.gcode)

    def save_to_file(self, filename):
        """
        Save the generated G code to a file.

        Args:
            filename (str): The name of the destination file.
        """

        # Ensure the filename has a .nc file extension.
        if not filename.endswith(".nc"):
            filename += ".nc"

        # Write the G code to the file.
        with open(filename, "w") as file:
            file.write(self.get_gcode())

        print(f"G code saved to {filename}")


# Example usage
if __name__ == "__main__":
    post_processor = GCodePostProcessor()
    post_processor.add_comment('MAIN PROGRAM - MACHINING OPERATIONS')
    post_processor.move_linear(x=10, y=20, z=5, feedrate=1500)
    post_processor.move_arc(x=15, y=25, i=2.5, j=2.5, clockwise=True, feedrate=1200)
    post_processor.move_linear(x=0, y=0, z=0, feedrate=1000)

    # Save the G code to a file
    post_processor.save_to_file("output.nc")
