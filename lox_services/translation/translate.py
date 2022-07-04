"""All functions used for translations."""

import os
from typing import Dict, Literal

from Algorithms.Configs.paths import TRANSLATIONS_FOLDER
from Algorithms.Services.translation.enums import TranslationModules
from Algorithms.Utils.formats import json_file_to_python_dictionary

AvailableLanguages = Literal['EN','FR','NL']


def get_translations(language: AvailableLanguages, module: TranslationModules = TranslationModules.ROOT, strict=False) -> Dict[str, str]:
    """Gets the translations for one language.
        ## Arguments
        - `language`: The language to get the translations from
        - `module`: The module to get the translations from. Default is TranslationModules.ROOT ('').
        - `strict`: If set to True, a language that is not implemented will raise an error. 
            If set to False (default) a language that is not implemented will return English translations, 
        
        ## Returns
        - A dictionnary of translations for one language
    """
    translations_module_folder = os.path.join(TRANSLATIONS_FOLDER, module.value)
    if language == 'NL':
        language = 'EN'
    
    try:
        json_file = os.path.join(translations_module_folder, f"{language}.json")
        translations = json_file_to_python_dictionary(json_file)
    
    except Exception as exception:
        if strict:
            raise exception 
        json_file = os.path.join(translations_module_folder, "EN.json")
        translations = json_file_to_python_dictionary(json_file)
    
    return translations


if __name__ == '__main__':
    print(get_translations("FR"))
