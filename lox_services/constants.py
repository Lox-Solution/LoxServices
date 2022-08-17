import os
from lox_services.config.paths import CONFIGS_FOLDER
from lox_services.utils.formats import json_file_to_python_dictionary

# These constants are stored in MainAlgorithms repository.

lox_dict = json_file_to_python_dictionary(os.path.join(CONFIGS_FOLDER,"lox_services_constants.json"))

ACCOUNTANT_EMAIL: str = lox_dict['ACCOUNTANT_EMAIL']
LOX_CC_EMAIL: str = lox_dict['LOX_CC_EMAIL']
LOX_FR_CC_EMAIL: str = lox_dict['LOX_FR_CC_EMAIL']
