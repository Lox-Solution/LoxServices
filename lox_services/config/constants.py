import os
from lox_services.config.paths import LOX_SERVICES_FOLDER
from lox_services.utils.formats import json_file_to_python_dictionary

# These constants are stored in MainAlgorithms repository, cause they contain sensitive information.

lox_dict = json_file_to_python_dictionary(os.path.join(LOX_SERVICES_FOLDER,"lox_services_constants.json"))

LOX_TEAM_EMAIL: str = lox_dict['LOX_TEAM_EMAIL']
LOX_FINANCE_EMAIL: str = lox_dict['LOX_FINANCE_EMAIL']
