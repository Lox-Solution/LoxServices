"""All functions used for translations."""

import os

from lox_services.utils import json_file_to_python_dictionary, print_error, print_success

TRANSLATIONS_FOLDER = os.path.join(os.path.dirname(__file__), "languages")

def check_all_translations_keys():
    """Checks that no key is missing from any translations."""
    past_language_translations = None
    past_file = None
    differences = []
    for file in os.listdir(TRANSLATIONS_FOLDER):
        # print(file)
        if not file.endswith(".json"):
            continue 
        
        file_path = os.path.join(TRANSLATIONS_FOLDER, file)
        language_translations = json_file_to_python_dictionary(file_path)
        if not (past_language_translations is None and past_file is None):
            print(f"Comparing keys between {past_file} and {file}")
            if past_language_translations.keys() != language_translations.keys():
                differences.append((past_file, file))
        
        past_language_translations = language_translations
        past_file = file
        
    if len(differences) > 0:
        print_error("Some keys are not matching")
        print(differences)
    else:
        print_success("All files have the same root translation keys.")
    return differences
