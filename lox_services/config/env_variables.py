import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


def get_env_variable(key: str) -> Any:
    """Gets the environment variable for a given key.
    ## Arguments
    - `key`: The key to get the environment variable
    ## Returns:
    - The value of the environment variable if it exists
    - Raises a ValueError otherwise
    """
    get_env = os.getenv(key)
    if get_env is None:
        raise ValueError(
            f"'{key}' key does not exist in .env file or in environment variables."
        )
    return get_env
