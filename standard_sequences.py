def get_example_title(units):
    """ Generate example title block. """
    title_block = ""
    title_block += "(Title: Spirograph Engraving)\n"
    title_block += "(Author: Erika Mustermann)\n"
    title_block += "(Date: MM-DD-YYYY)\n"
    title_block += "(Description: Four-lobed clover pattern)\n"

    if units == "in":
        setup_text = "(Setup: Home Z 0.25\" above stock surface)\n"
    else:
        setup_text = "(Setup: Home Z 6.35mm above stock surface)\n"

    title_block += setup_text
    title_block += "(Setup: Home XY at center of square stock)\n"

    if units == "in":
        tool_text = "(Cutting Tool: End mill, 2 flute, 1/16\" OD, 1/8\" LOC, carbide)\n"
    else:
        tool_text = "(Cutting Tool: End mill, 2 flute, 1.6mm OD, 3mm LOC, carbide)\n"

    title_block += tool_text

    return title_block


def get_start_sequence(units):
    """ Generate standard start sequence. """
    start_sequence = ""
    start_sequence += "(Start Sequence)\n"
    start_sequence += "G90 (use absolute distance mode)\n"

    if units == "in":
        length_unit_text = "G20 (use inch length units)\n"
    else:
        length_unit_text = "G21 (use mm length units)\n"

    start_sequence += length_unit_text
    start_sequence += "G94 (feed in units per minute)\n"
    start_sequence += "G80 (cancel any active canned cycle)\n"
    start_sequence += "G40 (cancel cutter radius compensation)\n"
    start_sequence += "G49 (cancel tool length compensation)\n"
    start_sequence += "G17 (set current plane to XY)\n"

    return start_sequence


def get_end_sequence(units, safe_Z):
    """ Generate standard end sequence. """
    end_sequence = ""
    end_sequence += "(End Sequence)\n"
    end_sequence += f"G00 Z{safe_Z} (rapid move to safe height)\n"
    end_sequence += "G00 X0 Y0 (rapid move to origin)\n"
    end_sequence += "M02 (end program)\n"

    return end_sequence


# Run the application
if __name__ == "__main__":
    print("Sample Title Block:")
    print("===============================")
    print(get_example_title("in"))

    print("Sample Start Sequence:")
    print("===============================")
    print(get_start_sequence("in"))

    print("Sample End Sequence:")
    print("===============================")
    print(get_end_sequence("in", 0.25))
