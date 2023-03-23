import base64
import gzip
from json import loads
from typing import Dict


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
