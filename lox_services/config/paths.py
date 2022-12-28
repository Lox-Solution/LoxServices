"""All global configuration variables"""
from os import getenv, path


# To find easily the root of the project. 
# Should be like this: "local_absolute_path/Main-Algorithms/Algorithms" 
ROOT_PATH: str = getenv("PYTHONPATH", "/")

_cloud_root_path = getenv("CLOUD_ROOT_PATH")
CLOUD_ROOT_PATH = _cloud_root_path if _cloud_root_path is not None else ROOT_PATH

# Folder where results will be stored. This folder is ignored by git.
OUTPUT_FOLDER: str = path.join(CLOUD_ROOT_PATH, "output_folder")

CHROMEDRIVER_PATH: str = path.join(ROOT_PATH, "chromedriver")
