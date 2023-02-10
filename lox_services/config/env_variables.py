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
    key = os.getenv(key)
    if key is None:
        raise ValueError(
            f"'{key}' key does not exist in .env file or in environment variables."
        )
    return key


if __name__ == "__main__":
    print(get_env_variable("FINANCE_REFRESH_TOKEN"))
