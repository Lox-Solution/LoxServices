from datetime import datetime
import os
import json
import sys
import tempfile
import shutil

from functools import reduce
from urllib.parse import urlparse

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import undetected_chromedriver as undetected_webdriver
from lox_services.config.env_variables import get_env_variable
from lox_services.config.paths import OUTPUT_FOLDER
from lox_services.persistence.storage.constants import SELENIUM_CRASHES_BUCKET
from lox_services.persistence.storage.storage import upload_file
from lox_services.utils.general_python import safe_mkdir
from lox_services.utils.chrome_version import get_chrome_version


def find_chrome_location():
    """Finds and returns the Chrome or Chromium executable location across OS."""
    locations = ["google-chrome", "chromium", "chrome"]

    if sys.platform == "darwin":  # macOS
        locations.extend(
            [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ]
        )
    elif sys.platform == "win32":  # Windows
        locations.extend(
            [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files\\Chromium\\Application\\chrome.exe",
            ]
        )

    for loc in locations:
        if not loc.startswith("/") and not loc.endswith(".exe"):
            path = shutil.which(loc)  # Search in PATH
        else:
            path = loc  # Use predefined path

        if path and os.path.exists(path):
            print(f"Chrome found via system search: {path}")
            return path  # Return first valid path found

    print("No Chrome installation found via system search.")
    return None  # No valid Chrome installation found


def get_chrome_binary_location():
    """Get Chrome binary location from env or fallback to system search."""
    try:
        chrome_location = get_env_variable("CHROME_BINARY_LOCATION")
        if not chrome_location:  # Handle empty or null values
            raise ValueError
        print(f"Chrome location set via environment variable: {chrome_location}")
    except ValueError:
        chrome_location = find_chrome_location()

    if not chrome_location:
        raise RuntimeError(
            "No valid Chrome binary found. Set CHROME_BINARY_LOCATION or install Chrome."
        )

    return chrome_location


def convert_proxy(proxy_url):
    parsed = urlparse(proxy_url)

    host = parsed.hostname
    port = parsed.port
    username = parsed.username
    password = parsed.password

    return (host, port, username, password)


class ProxyExtension:
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "76.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %d
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        { urls: ["<all_urls>"] },
        ['blocking']
    );
    """

    def __init__(self, host, port, user, password):
        self._dir = os.path.normpath(tempfile.mkdtemp())

        manifest_file = os.path.join(self._dir, "manifest.json")
        with open(manifest_file, mode="w") as f:
            f.write(self.manifest_json)

        background_js = self.background_js % (host, port, user, password)
        background_file = os.path.join(self._dir, "background.js")
        with open(background_file, mode="w") as f:
            f.write(background_js)

    @property
    def directory(self):
        return self._dir

    def __del__(self):
        shutil.rmtree(self._dir)


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
    proxy: str = None,
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
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)

    options.binary_location = get_chrome_binary_location()

    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    options.add_argument("--disable-popup-blocking")

    # Disable download popup blocking feature
    options.add_argument("--disable-features=DownloadPopupBlocking")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Disable search engine choice screen
    options.add_argument("--disable-search-engine-choice-screen")

    options.headless = False

    if proxy:
        proxy = convert_proxy(
            proxy_url=proxy
        )  # your proxy with auth, this one is obviously fake
        proxy_extension = ProxyExtension(*proxy)
        options.add_argument(f"--load-extension={proxy_extension.directory}")

    driver = ChromeWithPrefs(version_main=version, options=options)
    driver.set_window_size(size_length, size_width)

    # Handle download dialog
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_directory},
    }
    driver.execute("send_command", params)

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
    proxy: str = None,
):
    """Creates an undetected chromedriver with the wanted download folder.
    ## Arguments
    - `download_folder`: Folder where we want to download the invoices
    - `size_length`: Length of the chrome window
    - `size_width`: Width of the chrome window
    - `version`: Version of the chrome driver
    - `proxy`: Proxy to use

    ## Return
    - A well setup chrome driver
    """

    if get_env_variable("ENVIRONMENT") == "production":
        shutdown_current_instances()

    return init_chromedriver(download_folder, size_length, size_width, version, proxy)
