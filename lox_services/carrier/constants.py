from copy import deepcopy
from selenium.webdriver.chrome.options import Options

_options = Options()
_options.add_argument("--no-sandbox")
_options.add_argument("--disable-dev-shm-usage")
_options.add_argument("--start-maximized")

CHROME_OPTIONS = deepcopy(_options)
