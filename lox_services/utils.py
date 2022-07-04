from json import loads
from typing import Dict
from enum import Enum

class Colors(Enum):
    """Enumeration that stores some colors."""
    # pylint: disable=invalid-name
    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Magenta = 35
    Cyan = 36
    White = 37
    
def colorize(string: str, color: Colors):
    """Format a string to print it with a certain color in the terminal."""
    return f"\x1b[{color.value}m{string}\x1b[0m"

def print_error(string: str):
    """Format a string to error style."""
    print(colorize(string, Colors.Red))

def print_success(string: str):
    """Format a string to a success style."""
    print(colorize(string, Colors.Green))

def json_file_to_python_dictionary(file_path: str) -> Dict[str, str] :
    """Convert a json file to python dictionary.
        ## Arguments
        - `file_path`: The absolute path of the file to extract
    """
    json_file = open(file_path, 'r')
    with json_file:
        dictionnary = loads(json_file.read())
    
    return dictionnary