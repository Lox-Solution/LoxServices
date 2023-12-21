from datetime import datetime
import os
import json
import shutil
import time
import tempfile
from functools import reduce

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import undetected_chromedriver as undetected_webdriver

from lox_services.config.env_variables import get_env_variable
from lox_services.config.paths import OUTPUT_FOLDER
from lox_services.persistence.storage.constants import SELENIUM_CRASHES_BUCKET
from lox_services.persistence.storage.storage import upload_file
from lox_services.scraping.chromedriver_utils import (
    add_cookies_from_json,
    get_chrome_options,
    get_chrome_profile_folder,
)
from lox_services.utils.general_python import safe_mkdir
from lox_services.utils.chrome_version import get_chrome_version


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
                    file_path = os.path.join(OUTPUT_FOLDER, "screenshot", file_name)
                    safe_mkdir(file_path)
                    self.get_screenshot_as_file(file_path)
                    upload_file(SELENIUM_CRASHES_BUCKET, file_path, file_name)
                    screenshot = f"https://storage.cloud.google.com/{SELENIUM_CRASHES_BUCKET}/{file_name}?authuser=0"
                    os.remove(file_path)
                except Exception:
                    print("Can't take screenshot.")
                    pass
                if screenshot:
                    exc_val.msg += f"\n Screenshot : {screenshot}"
        self.quit()


def init_chromedriver(
    download_directory: str,
    size_length: int,
    size_width: int,
    version: int,
    cookies: dict,
) -> webdriver.Chrome:
    """Generates default chrome options for the given download directory.
    ## Arguments
        - `download_folder`: Folder where we want to download the invoices
        - `size_length`: Length of the chrome window
        - `size_width`: Width of the chrome window
        - `version`: Version of the chrome driver to use
        - `cookies`: Cookies to add to the driver

    ## Returns
    - The well setup driver
    """
    shutdown_current_instances()

    folder_path = get_chrome_profile_folder()
    profile_name = "Lox"

    if cookies:
        profile_folder_path = os.path.join(folder_path, profile_name)

        # Delete the profile if already existing
        if os.path.exists(profile_folder_path):
            shutil.rmtree(profile_folder_path)

        # Create a new profile
        driver = ChromeWithPrefs(
            version_main=version,
            options=get_chrome_options(download_directory),
            user_data_dir=folder_path,
            user_profile=profile_name,
        )
        driver.get("https://www.github.com")
        shutdown_current_instances()
        # Add cookies to newly created profile
        add_cookies_from_json(
            profile_folder_path,
            cookies,
        )

    driver = ChromeWithPrefs(
        version_main=version,
        options=get_chrome_options(download_directory),
    )
    driver.set_window_size(size_length, size_width)

    return driver


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
    version: int = get_chrome_version(),
    cookies: dict = None,
):
    """Creates an undetected chromedriver with the wanted download folder.
    ## Arguments
    - `download_folder`: Folder where we want to download the invoices
    - `size_length`: Length of the chrome window
    - `size_width`: Width of the chrome window
    - `version`: Version of the chrome driver to use
    - `cookies`: Cookies to add to the driver

    ## Return
    - A well setup chrome driver
    """
    if get_env_variable("ENVIRONMENT") == "production":
        shutdown_current_instances()

    return init_chromedriver(download_folder, size_length, size_width, version, cookies)
