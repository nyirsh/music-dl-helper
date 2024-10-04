"""Module that provides couple of utilities for strings"""

import re


def is_string_none_or_empty(text: str | None):
    """
    Returns True if the string is either None or has a lenght of 0
    """
    return text is None or (isinstance(text, str) and len(text) == 0)


def get_first_string_line(multi_line_string: str | None):
    """
    Returns the first non empty line of a string that contains multiple lines,
    while also removing all ansi codes
    """
    # If it's not a string, simply returns None
    if is_string_none_or_empty(multi_line_string):
        return None

    # Filter out empty lines
    non_empty_lines = get_all_non_empty_lines(multi_line_string)

    # Return the first non-empty line, or None if there are no non-empty lines
    return non_empty_lines[0] if non_empty_lines else None


def get_last_string_line(multi_line_string: str | None):
    """
    Returns the last non empty line of a string that contains multiple lines,
    while also removing all ansi codes
    """
    # If it's not a string, simply returns None
    if is_string_none_or_empty(multi_line_string):
        return None

    # Filter out empty lines
    non_empty_lines = get_all_non_empty_lines(multi_line_string)
    # Return the last non-empty line, or None if there are no non-empty lines
    return non_empty_lines[-1] if non_empty_lines else None


def get_all_non_empty_lines(multi_line_string: str | None):
    """
    Returns the non empty line of a string that contains multiple lines,
    while also removing all ansi codes
    """
    # If it's not a string, simply returns None
    if is_string_none_or_empty(multi_line_string):
        return None

    # Split the string into lines and strip whitespace
    lines = [remove_ansi_codes(line).strip()
             for line in multi_line_string.splitlines()]

    # Filter out empty lines
    non_empty_lines = [line for line in lines if line]
    return non_empty_lines


def remove_ansi_codes(text: str):
    """
    Removes all ansi codes that manipulate the console colors etc
    """
    # If it's not a string, simply returns an empty string
    if is_string_none_or_empty(text):
        return ""

    # Uses a regex to remove all instances of ansi codes
    ansi_escape_pattern = re.compile(r'\x1B\[[0-?9;]*[mK]')
    return ansi_escape_pattern.sub('', text)
