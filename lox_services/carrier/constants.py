from selenium.webdriver.chrome.options import Options

def get_chromedriver_options():
    """Returns the options for the chromedriver"""
    _options = Options()
    _options.add_argument("--no-sandbox")
    _options.add_argument("--disable-dev-shm-usage")
    _options.add_argument("--start-maximized")

    chrome_prefs = {}
    _options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}

    return _options


CHROME_OPTIONS = get_chromedriver_options()
