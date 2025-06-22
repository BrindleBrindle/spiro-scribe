def validate_int_pos(value):
    """
    Validate the input to ensure it is an integer greater than zero.

    Args:
        value (str): Input value to evaluate.

    Returns:
        bool: True if the input is a valid int or empty, False otherwise.
    """
    if value == "":  # allow empty string (to enable deletion)
        return True
    try:
        return True if int(value) > 0 else False
    except ValueError:
        return False  # reject input if it's not a valid int


def validate_float_pos(value):
    """
    Validate the input to ensure it is a float greater than zero.

    Args:
        value (str): Input value to evaluate.

    Returns:
        bool: True if the input is a valid float or empty, False otherwise.
    """
    if value == "":  # allow empty string (to enable deletion)
        return True
    try:
        return True if float(value) > 0 else False
    except ValueError:
        return False  # reject input if it's not a valid float


def validate_float(value):
    """
    Validate the input to ensure it is a float.

    Args:
        value (str): Input value to evaluate.

    Returns:
        bool: True if the input is a valid float or empty, False otherwise.
    """
    if value == "":  # allow empty string (to enable deletion)
        return True
    try:
        return True if float(value) > 0 else False
    except ValueError:
        return False  # reject input if it's not a valid float


def validate_resolution(value):
    """
    Validate the input to ensure it is a valid path resolution value.

    Args:
        value (str): Input value to evaluate.

    Returns:
        bool: True if the input is a valid resolution or empty, False otherwise.
    """
    if value == "":  # allow empty string (to enable deletion)
        return True
    try:
        return True if (int(value) > 0) and (int(value) <= 5000) else False
    except ValueError:
        return False  # reject input if it's not a valid int


def validate_passes(value):
    """
    Validate the input to ensure it is a valid number of cut passes.

    Args:
        value (str): Input value to evaluate.

    Returns:
        bool: True if the input is a valid number of passes or empty, False otherwise.
    """
    if value == "":  # allow empty string (to enable deletion)
        return True
    try:
        return True if (int(value) > 0) and (int(value) <= 100) else False
    except ValueError:
        return False  # reject input if it's not a valid int
