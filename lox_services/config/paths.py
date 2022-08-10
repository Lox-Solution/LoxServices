"""All global configuration variables"""
from os import getenv, path

# from Algorithms.Utils.general_python import print_success, print_error

# To find easily the root of the project. 
# Should be like this: "local_absolute_path/Main-Algorithms/Algorithms" 
ROOT_PATH: str = getenv("PYTHONPATH")

# Folder where results will be stored. This folder is ignored by git.
OUTPUT_FOLDER: str = path.join(ROOT_PATH, "output_folder")

ASSETS_FOLDER: str = path.join(ROOT_PATH, "Algorithms", "Assets")


if __name__ == "__main__":
    print("Testing configuration variables...")
    try:
        print("ROOT_PATH:",ROOT_PATH)
        assert ROOT_PATH.endswith("/Main-Algorithms"), "ROOT_PATH"
        
        print("OUTPUT_FOLDER:",OUTPUT_FOLDER)
        assert OUTPUT_FOLDER.startswith(ROOT_PATH), "OUTPUT_FOLDER"
        
        print("Configuration file is valid.")
        
    except AssertionError as assertion_error:
        print(f"Configuration file is not valid, assertion error: {assertion_error.args[0]}")
