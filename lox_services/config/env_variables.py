import os
from typing import Dict

from lox_services.config.paths import ROOT_PATH
from lox_services.utils.general_python import print_error

def _get_key_and_value(string: str):
    splited = string.split("=",maxsplit=1)
    if len(splited) == 2:
        key: str = splited[0]
        value: str = splited[1].split("#", maxsplit=1)[0] # remove comments
        return key.strip(), value.strip()
    return None, None


def _get_env_variables_from_file() -> Dict[str,str]:
    with open(os.path.join(ROOT_PATH, ".env"), "r") as txt_file:
        pairs = list(set(map(_get_key_and_value,txt_file.readlines())))
        return pairs


def _get_env_variables_as_dict():
    file_env_variables = _get_env_variables_from_file()
    dictionary = dict(file_env_variables)
    
    #Add env variables
    dictionary.update(os.environ)
    
    #Remove useless and/or heavy stuff
    try:
        dictionary.pop(None)
        dictionary.pop("LS_COLORS")
        dictionary.pop("PS1")
    except KeyError:
        pass
    
    return dictionary


def get_env_variable(key: str):
    """Gets the environment variable for a given key.
        ## Arguments
        - `key`: The key to get the environment variable
        ## Returns:
        - The value of the environment variable if it exists
        - Raises a KeyError exception otherwise
    """
    all_variables = _get_env_variables_as_dict()
    try:
        value = all_variables[key]
        return value
    except KeyError as exception:
        print_error(f"'{key}' key does not exist in .env file or in environment variables.")
        raise exception
