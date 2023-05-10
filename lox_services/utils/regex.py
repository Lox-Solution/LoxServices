import re
from typing import Any, Callable, Optional


def make_get_first(
    regex_string: str, process_match: Optional[Callable] = None
) -> Callable[[str], Any]:
    """
    Factory function that returns a callable that takes a string as an argument and
    returns the first match for a given regular expression pattern within that string.

    Args:
    regex_string (str): A regular expression pattern to match against strings.
    process_match (Optional[Callable]): A function that takes the match as input and returns a processed result
    (say, to coerce a data type). If provided, the returned callable will apply this function to the match
    before returning it.

    Returns:
    A callable that takes a string argument and returns the first match of the pattern
    within the string.

    Example usage:

    >>>import re
    >>>get_first_digit = make_get_first(r"\d+")
    >>>print(get_first_digit('abc 123 def 456'))  # Output: '123'

    """
    pattern = re.compile(regex_string)

    def get_first(string: str) -> Any:
        """
        This function takes a string as an argument and returns the first match for the pattern within
        that string.

        Args:
        string (str): A string to search for a match to the pattern.

        Returns:
        The first match of the pattern within the string.
        """
        try:
            match = pattern.search(string).group()
        except AttributeError as e:
            raise AttributeError(
                "Unable to find any value matching the regular expression"
            ) from e
        if process_match is not None:
            match = process_match(match)
        return match

    return get_first
