from datetime import datetime
import os
import json
import tempfile
from functools import reduce

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import undetected_chromedriver as undetected_webdriver

from lox_services.config.env_variables import get_env_variable
from lox_services.config.paths import OUTPUT_FOLDER
from lox_services.persistence.storage.constants import SELENIUM_CRASHES_BUCKET
from lox_services.persistence.storage.storage import upload_file


class ChromeWithPrefs(undetected_webdriver.Chrome):
    """Creates a ChromeDriver instance with the specified options."""

    def __init__(self, *args, options=None, **kwargs):
        if options:
            self._handle_prefs(options)

        super().__init__(*args, options=options, **kwargs)

        # remove the user_data_dir when quitting
        self.keep_user_data_dir = False

    @staticmethod
    def _handle_prefs(options):
        if prefs := options.experimental_options.get("prefs"):
            # turn a (dotted key, value) into a proper nested dict
            def undot_key(key, value):
                if "." in key:
                    key, rest = key.split(".", 1)
                    value = undot_key(rest, value)
                return {key: value}

            # undot prefs dict keys
            undot_prefs = reduce(
                lambda d1, d2: {**d1, **d2},  # merge dicts
                (undot_key(key, value) for key, value in prefs.items()),
            )

            # create an user_data_dir and add its path to the options
            user_data_dir = os.path.normpath(tempfile.mkdtemp())
            options.add_argument(f"--user-data-dir={user_data_dir}")

            # create the preferences json file in its default directory
            default_dir = os.path.join(user_data_dir, "Default")
            os.mkdir(default_dir)

            prefs_file = os.path.join(default_dir, "Preferences")
            with open(prefs_file, encoding="latin1", mode="w") as f:
                json.dump(undot_prefs, f)

            # pylint: disable=protected-access
            # remove the experimental_options to avoid an error
            del options._experimental_options["prefs"]

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, WebDriverException):
            if get_env_variable("ENVIRONMENT") == "production":
                screenshot = None
                print("Exception Raised, try to save window screenshot.")
                try:
                    timestamp = datetime.now().timestamp()
                    file_name = str(timestamp).replace(".", "_") + ".png"
                    upload_file(
                        SELENIUM_CRASHES_BUCKET, self.get_screenshot_as_png(), file_name
                    )
                    screenshot = f"https://storage.cloud.google.com/{SELENIUM_CRASHES_BUCKET}/{file_name}?authuser=0"
                except Exception:
                    print("Can't take screenshot.")
                    pass
                if screenshot:
                    exc_val.msg += f"\n Screenshot : {screenshot}"
        self.quit()


def init_chromedriver(
    download_directory: str, size_length: int, size_width: int, version: int
) -> webdriver.Chrome:
    """Generates default chrome options for the given download directory.
    ## Arguments
        - `download_folder`: Folder where we want to download the invoices
        - `size_length`: Length of the chrome window
        - `size_width`: Width of the chrome window

    ## Returns
    - The well setup driver
    """
    prefs = {
        "download.default_directory": download_directory,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
    }
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)

    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--incognito")
    options.add_argument(f"--window-size={size_length},{size_width}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Chnage the the version here to match version on main VM
    return ChromeWithPrefs(version_main=version, options=options)


def shutdown_current_instances():
    """Shutdown current Chrome and Chromium processes Unix OS."""
    os.system("killall -9 'Google Chrome'")
    os.system("killall -9 'Chromium'")
    os.system("pkill chromium")
    os.system("pkill chrome")


def run_chromedriver(
    download_folder: str = OUTPUT_FOLDER,
    size_length: int = 960,
    size_width: int = 960,
    version: int = 109,
):
    """Creates an undetected chromedriver with the wanted download folder.
    ## Arguments
    - `download_folder`: Folder where we want to download the invoices
    - `size_length`: Length of the chrome window
    - `size_width`: Width of the chrome window

    ## Return
    - A well setup chrome driver
    """
    if get_env_variable("ENVIRONMENT") == "production":
        shutdown_current_instances()
    return init_chromedriver(download_folder, size_length, size_width, version)
