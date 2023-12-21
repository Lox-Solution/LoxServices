import base64
import os
import platform
import sqlite3
from typing import Any, Dict, List

from selenium import webdriver


def add_cookies_from_json(dest: str, cookies: List[Dict[str, Any]]) -> None:
    """Adds cookies from a JSON file to the destination database.

    Args:
        dest: The destination folder where the cookies database is located.
        cookies: The list of cookies to be added.

    Returns:
        None.
    """
    dest_cookies_db = os.path.join(dest, "Cookies")
    print(dest_cookies_db)
    # Connect to the destination cookies database
    conn_dest = sqlite3.connect(dest_cookies_db)
    cursor_dest = conn_dest.cursor()
    # Read cookies from JSON file

    # Insert cookies into the destination database
    for cookie in cookies:
        # Decode the Base64 encoded encrypted_value
        encrypted_value = (
            base64.b64decode(cookie["encrypted_value"])
            if "encrypted_value" in cookie
            else b""
        )
        cookie_tuple = (
            cookie.get("creation_utc"),
            cookie.get("host_key"),
            cookie.get("top_frame_site_key", ""),
            cookie.get("name"),
            cookie.get("value"),
            encrypted_value,
            cookie.get("path"),
            cookie.get("expires_utc"),
            cookie.get("is_secure"),
            cookie.get("is_httponly"),
            cookie.get("last_access_utc"),
            cookie.get("has_expires"),
            cookie.get("is_persistent"),
            cookie.get("priority"),
            cookie.get("samesite", 0),  # Default to 0 if not present
            cookie.get("source_scheme", 0),
            cookie.get("source_port", 0),
            cookie.get("is_same_party", 0),
            cookie.get("last_update_utc", 0),
        )
        cursor_dest.execute(
            "INSERT OR IGNORE INTO cookies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            cookie_tuple,
        )
    conn_dest.commit()
    # Close connection
    cursor_dest.close()
    conn_dest.close()
    print("Cookies added successfully from JSON file.")


def get_chrome_options(download_directory: str) -> webdriver.ChromeOptions:
    """Returns Chrome options with specified preferences for download directory.

    Args:
        download_directory: The directory where downloads should be saved.

    Returns:
        Chrome options with specified preferences.
    """
    options = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": download_directory,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
        "excludeSwitches": ["disable-popup-blocking"],
    }

    options.add_experimental_option("prefs", prefs)
    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    options.add_argument("--disable-popup-blocking")

    # Remove the popup that ask to download the file
    # https://stackoverflow.com/questions/77093248/chromedriver-version-117-forces-save-as-dialog-how-to-bypass-selenium-jav
    options.add_argument("--disable-features=DownloadBubble,DownloadBubbleV2")
    # Remove popup to select privacy
    options.add_argument("--disable-features=SafeBrowsingEnhancedProtection")
    options.add_argument("--disable-features=PrivacySandboxSettings4")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.headless = False

    return options


def get_chrome_profile_folder() -> str:
    """Returns the path to the Chrome profile folder based on the operating system and profile name.

    Returns:
        The path to the Chrome profile folder.

    Raises:
        Exception: If the operating system is not supported.
    """
    system = platform.system()

    if system == "Linux":
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".config/google-chrome")
    elif system == "Darwin":  # macOS
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, "Library/Application Support/Google/Chrome")
    else:
        raise Exception("Unsupported operating system")
