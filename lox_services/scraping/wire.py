from seleniumwire import webdriver
import seleniumwire.undetected_chromedriver as uc

"""SeleniumWire is different from our original chromedriver:
It intercepts and captures all HTTP requests and responses made by the WebDriver browser, including AJAX calls, images, scripts, and more. This enables you to analyze and modify the network traffic as needed.
"""


def run_simple_seleniumware_chromedriver():
    """Creates an instance of seleniumwire chrome driver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return uc.Chrome(
        seleniumwire_options={},
        options=options,
    )
