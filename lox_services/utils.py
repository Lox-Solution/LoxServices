from json import loads
from typing import Dict

def json_file_to_python_dictionary(file_path: str) -> Dict[str, str] :
    """Convert a json file to python dictionary.
        ## Arguments
        - `file_path`: The absolute path of the file to extract
    """
    json_file = open(file_path, 'r')
    with json_file:
        dictionnary = loads(json_file.read())
    
    return dictionnary