from selenium.webdriver.chrome.options import Options

def get_chromedriver_options():
    """Returns the options for the chromedriver"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")

    return options


CHROME_OPTIONS = get_chromedriver_options()
