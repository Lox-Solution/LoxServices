from lox_services.scraping.chromedriver import (
    get_chrome_binary_location,
    shutdown_current_instances,
)
from selenium_stealth import stealth
import undetected_chromedriver as uc


from selenium.webdriver.chrome.options import Options
from lox_services.config.env_variables import get_env_variable
from lox_services.config.paths import OUTPUT_FOLDER

from lox_services.utils.chrome_version import get_chrome_version


def run_stealth_chromedriver(
    download_folder: str = OUTPUT_FOLDER,
    size_length: int = 960,
    size_width: int = 960,
    version: int = get_chrome_version(),
):
    if get_env_variable("ENVIRONMENT") == "production":
        shutdown_current_instances()

    chrome_options = Options()
    chrome_options.binary_location = get_chrome_binary_location()
    chrome_options.add_argument(
        "--no-first-run --no-service-autorun --password-store=basic"
    )
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    chrome_options.add_argument("--disable-features=DownloadPopupBlocking")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.headless = False

    # Define prefs
    chrome_prefs = {
        "download.default_directory": download_folder,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }

    # Set preferences using desired capabilities
    capabilities = {"goog:chromeOptions": {"prefs": chrome_prefs}}

    # Initialize UC with capabilities
    driver = uc.Chrome(
        options=chrome_options, desired_capabilities=capabilities, version_main=version
    )

    driver.set_window_size(size_length, size_width)

    # Handle download dialog
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_folder},
    }
    driver.execute("send_command", params)

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver
