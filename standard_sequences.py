import inspect


def get_example_title(units):
    """ Generate example title block. """
    title_block = ""
    title_block += "\t(DESCRIPTION)\n"
    title_block += "\t(Title: Spirograph Engraving)\n"
    title_block += "\t(Author: Erika Mustermann)\n"
    title_block += "\t(Date: MM-DD-YYYY)\n"
    title_block += "\t(Description: Four-lobed clover pattern)\n"

    if units == "imperial":
        setup_text = "\t(Setup: Home Z 0.25\" above stock surface)\n"
    else:
        setup_text = "\t(Setup: Home Z 6.35mm above stock surface)\n"

    title_block += setup_text
    title_block += "\t(Setup: Home XY at center of square stock)\n"

    if units == "imperial":
        tool_text = "\t(Cutting Tool: End mill, 2 flute, 1/16\" OD, 1/8\" LOC, carbide)\n"
    else:
        tool_text = "\t(Cutting Tool: End mill, 2 flute, 1.6mm OD, 3mm LOC, carbide)"

    title_block += tool_text

    return title_block.strip()  # strip away any trailing whitespace


def get_start_sequence(units):
    """ Generate standard start sequence. """
    start_sequence = ""
    start_sequence += "(START SEQUENCE)\n"
    start_sequence += "\tG90 (use absolute distance mode)\n"

    if units == "imperial":
        length_unit_text = "\tG20 (use inch length units)\n"
    else:
        length_unit_text = "\tG21 (use mm length units)\n"

    start_sequence += length_unit_text
    start_sequence += "\tG94 (feed in units per minute)\n"
    start_sequence += "\tG80 (cancel any active canned cycle)\n"
    start_sequence += "\tG40 (cancel cutter radius compensation)\n"
    start_sequence += "\tG49 (cancel tool length compensation)\n"
    start_sequence += "\tG17 (set current plane to XY)"

    return start_sequence.strip()  # strip away any trailing whitespace


def get_end_sequence():
    """ Generate standard end sequence. """
    end_sequence = ""
    end_sequence += "(END SEQUENCE)\n"
    end_sequence += "\tG00 Z<safe_Z> (rapid move to safe height)\n"
    end_sequence += "\tG00 X0 Y0 (rapid move to origin)\n"
    end_sequence += "\tM02 (end program)"

    return end_sequence.strip()  # strip away any trailing whitespace


# Create a dictionary to map keys to functions
function_mapping = {
    "title": get_example_title,
    "start": get_start_sequence,
    "end": get_end_sequence,
}


def get_sequence(key, *args, **kwargs):
    # Use the dictionary to select the correct function
    func = function_mapping.get(key)
    if not func:
        raise ValueError(f"No function found for key: {key}")

    # Inspect the function's signature to determine its parameters
    sig = inspect.signature(func)
    if len(sig.parameters) == 0:
        # Call the function without arguments
        return func()
    else:
        # Call the function with provided arguments
        return func(*args, **kwargs)


# Run the application
if __name__ == "__main__":
    print("Sample Title Block:")
    print("===============================")
    print(get_sequence("title", "imperial"))
    print("")

    print("Sample Start Sequence:")
    print("===============================")
    print(get_sequence("start", "imperial"))
    print("")

    print("Sample End Sequence:")
    print("===============================")
    print(get_sequence("end"), "imperial")
