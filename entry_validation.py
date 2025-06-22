def validate_int_pos(new_value):
    """
    Validates the input to ensure it is an integer greater than zero.

    Args:
        new_value (str): The current value of the Entry widget after the change.

    Returns:
        bool: True if the input is a valid int or empty, False otherwise.
    """
    if new_value == "":  # Allow empty string (to enable deletion)
        return True
    try:
        return True if int(new_value) > 0 else False
    except ValueError:
        return False  # Reject input if it's not a valid int


def validate_float_pos(new_value):
    """
    Validates the input to ensure it is a float greater than zero.

    Arguments:
        new_value (str): The current value of the Entry widget after the change.

    Returns:
        bool: True if the input is a valid float or empty, False otherwise.
    """
    if new_value == "":  # Allow empty string (to enable deletion)
        return True
    try:
        return True if float(new_value) > 0 else False
    except ValueError:
        return False  # Reject input if it's not a valid float


def validate_resolution(new_value):
    """
    Validates the input to ensure it is a valid arc resolution value.

    Args:
        new_value (str): The current value of the Spinbox widget after the change.

    Returns:
        bool: True if the input is a valid resolution or empty, False otherwise.
    """
    if new_value == "":  # Allow empty string (to enable deletion)
        return True
    try:
        return True if (int(new_value) > 0) and (int(new_value) <= 5000) else False
    except ValueError:
        return False  # Reject input if it's not a valid int
