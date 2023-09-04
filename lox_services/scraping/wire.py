from seleniumwire import webdriver
import seleniumwire.undetected_chromedriver as uc

"""SeleniumWire is different from our original chromedriver:
It intercepts and captures all HTTP requests and responses made by the WebDriver browser, including AJAX calls, images, scripts, and more. This enables you to analyze and modify the network traffic as needed.
"""


def run_simple_chromedriver():
    """Creates an instance of seleniumwire chrome driver."""
    options = webdriver.ChromeOptions()

    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")

    return uc.Chrome(
        seleniumwire_options={},
        options=options,
    )
