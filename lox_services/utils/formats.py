import io
import gzip
import base64
import pandas as pd
from json import loads
from typing import Dict
from lox_services.utils.general_python import print_error


def json_file_to_python_dictionary(file_path: str) -> Dict[str, str]:
    """Convert a json file to python dictionary.
    ## Arguments
    - `file_path`: The absolute path of the file to extract
    """
    json_file = open(file_path, "r")
    with json_file:
        dictionnary = loads(json_file.read())

    return dictionnary


def image_to_base64(image_path: str) -> str:
    """Convert an image to base64 string."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode("utf-8")


def gzip_to_csv(infile, tofile):
    with open(infile, "rb") as inf, open(tofile, "w", encoding="utf8") as tof:
        decom_str = gzip.decompress(inf.read()).decode("utf-8")
        tof.write(decom_str)


def decode_base64_to_dataframe(base64_string: str) -> pd.DataFrame:
    """
    Decode a Base64-encoded CSV string and return it as a Pandas DataFrame.

    Args:
        base64_string (str): A Base64-encoded CSV string.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the data from the CSV string.
    """
    try:
        # Decoding the Base64 content
        decoded_csv = base64.b64decode(base64_string).decode("utf-8")

        # Converting the decoded CSV string to a DataFrame
        df = pd.read_csv(io.StringIO(decoded_csv))

        return df
    except Exception as e:
        print_error("Error while decoding Base64 string to DataFrame.")
        raise e
