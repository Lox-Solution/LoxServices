"""All global configuration variables"""
from os import getenv, path

# To find easily the root of the project. 
# Should be like this: "local_absolute_path/Main-Algorithms/Algorithms" 
ROOT_PATH: str = getenv("PYTHONPATH")

# Folder where results will be stored. These folders are ignored by git.
OUTPUT_FOLDER: str = path.join(ROOT_PATH, "output_folder")

CHROMEDRIVER_PATH: str = path.join(ROOT_PATH, "chromedriver")
