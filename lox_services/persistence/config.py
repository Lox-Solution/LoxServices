import os

from lox_services.config.env_variables import get_env_variable
from lox_services.config.paths import CLOUD_ROOT_PATH

ENVIRONMENT = get_env_variable("ENVIRONMENT")

if ENVIRONMENT == "production":
    service_account_name = get_env_variable("PRODUCTION_SERVICE_ACCOUNT")

elif ENVIRONMENT == "development":
    service_account_name = get_env_variable("DEVELOPMENT_SERVICE_ACCOUNT")

else:
    raise Exception("Please activate your environment with the activation script.")
    
SERVICE_ACCOUNT_PATH: str = os.path.join(CLOUD_ROOT_PATH, f"{service_account_name}.json")
