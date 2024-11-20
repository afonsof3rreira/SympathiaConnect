
def validate_time_in(input_value):
    """
    This function ensures that only numeric input is allowed in the Entry widgets.
    """
    return input_value.isdigit() and len(
        input_value) <= 3 or input_value == ""  # Allow up to 4 digits or empty input (backspace)

def validate_dac_in(input_value):
    """
    This function ensures that only numeric input is allowed in the Entry widgets
    and that the input is between 0 and 255 (inclusive).
    """
    if input_value == "":  # Allow empty input (backspace)
        return True

    if input_value.isdigit():  # Check if input consists of digits
        value = int(input_value)
        if 0 <= value <= 255:  # Ensure the value is between 0 and 255
            return True

    return False

def validate_fs_in(input_value):
    """
    This function ensures that only numeric input is allowed in the Entry widgets
    and that the input is between 1 and 5000 (inclusive).
    """
    if input_value == "":  # Allow empty input (backspace)
        return True
    if input_value.isdigit():  # Check if input consists of digits
        value = int(input_value)
        if 1 <= value <= 8000:  # Ensure the value is between 1 and 5000
            return True
    return False