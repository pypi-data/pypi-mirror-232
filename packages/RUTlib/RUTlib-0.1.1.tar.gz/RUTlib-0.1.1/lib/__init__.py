import re
import random


def clean_rut(rut: str) -> str:
    """
    Delete all non-numeric characters from a RUT.
    :param rut: RUT string
    :return: RUT without non-numeric characters.
    """
    cleaned_rut = re.sub(r'^(0+)(?=\d)|[^0-9kK]+', '', rut).upper() if isinstance(rut, str) else ''
    return cleaned_rut



def validate_rut(rut):
    """
    Verify if a RUT is valid.
    :param rut: RUT string
    :return: True if RUT is valid, False otherwise.
    """
    # rut to upper case
    rut = rut.upper()
    if re.match(r'^0+', rut):
        return False
    if not re.match(r'^0*(\d{1,3}(\.?\d{3})*)-?([\dkK])$', rut):
        return False

    cleaned_rut = clean_rut(rut)
    rut_numbers = int(cleaned_rut[:-1])
    rut_last_digit = cleaned_rut[-1]

    M = 0
    S = 1
    while rut_numbers:
        S = (S + (rut_numbers % 10) * (9 - (M % 6))) % 11
        rut_numbers = rut_numbers // 10
        M += 1

    last_digit_valid = str(10 if S == 0 else S - 1) if S != 11 else 'K'
    if (last_digit_valid == '10'):
        last_digit_valid = 'K'
    return last_digit_valid == rut_last_digit


def get_last_digit_of_rut(rut_numbers):
    """
    Get the verification digit of a RUT.
    :param rut_numbers: RUT numbers
    :return: RUT last digit.
    """
    M = 0
    S = 1
    while rut_numbers:
        S = (S + (rut_numbers % 10) * (9 - (M % 6))) % 11
        rut_numbers = rut_numbers // 10
        M += 1
    
    return str(10 if S == 0 else S - 1) if S != 11 else 'K'


def format_rut(rut, with_dots=True):
    """
    Format a RUT to a valid format.
    :param rut: RUT string
    :param with_dots: True if RUT should be formatted with dots, False otherwise.
    :return: RUT formatted.
    """
    rut = clean_rut(rut)
    
    if len(rut) == 1:
        return rut  # Return the verification digit as is
    
    rut_number = rut[:-1][::-1]  # Reverse the rut_number
    rut_verification = rut[-1]
    
    if with_dots:
        # Insert a dot every 3 characters
        rut_number = '.'.join([rut_number[i:i+3] for i in range(0, len(rut_number), 3)])
    
    return f"{rut_number[::-1]}-{rut_verification}"  # Reverse rut_number back



def generate_rut(length=8, formatted=True):
    """
    Generate a RUT with a random number.
    :param length: RUT length (including the verification digit)
    :param formatted: True if RUT should be formatted, False otherwise.
    :return: RUT generated.
    """
    
    # If the length is less than or equal to 1, return an empty string
    if length <= 1:
        return ''
    
    # Generate a random number with length-1 digits
    rut_numbers = random.randint(10**(length-2), 10**(length-1) - 1)
    
    # Get the verification digit for the generated number
    rut_last_digit = get_last_digit_of_rut(rut_numbers)
    if (rut_last_digit == '10'):
        rut_last_digit = 'K'
    # If not formatted, concatenate and return
    if not formatted:
        return str(rut_numbers) + rut_last_digit
    
    # Else format the RUT
    return format_rut(str(rut_numbers) + rut_last_digit)