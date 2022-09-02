from copy import deepcopy
from selenium.webdriver.chrome.options import Options

_options = Options()
# _options.add_argument("--headless")
_options.add_argument("--start-maximized")
_options.add_argument("--no-sandbox")

CHROME_OPTIONS = deepcopy(_options)
