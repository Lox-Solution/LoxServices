"""All global configuration variables"""
from os import getenv, path

from lox_services.config.env_variables import get_env_variable

# To find easily the root of the project. 
# Should be like this: "local_absolute_path/Main-Algorithms/Algorithms" 
ROOT_PATH: str = getenv("PYTHONPATH", "/")

try:
    CLOUD_ROOT_PATH = get_env_variable("CLOUD_ROOT_PATH")
except KeyError:
    CLOUD_ROOT_PATH = ROOT_PATH

# Folder where results will be stored. This folder is ignored by git.
OUTPUT_FOLDER: str = path.join(CLOUD_ROOT_PATH, "output_folder")

CHROMEDRIVER_PATH: str = path.join(ROOT_PATH, "chromedriver")
