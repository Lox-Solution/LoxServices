from copy import deepcopy
from selenium.webdriver.chrome.options import Options

_options = Options()
_options.add_argument("--start-maximized")
_options.add_argument("--no-sandbox")
_options.add_argument("--disable-dev-shm-usage")

CHROME_OPTIONS = deepcopy(_options)
