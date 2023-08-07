"""
All Utils function for Selenium use.
The name of the file is explicit to not confuse it with the PIP selenium package.
"""
import os
import time
import random
from enum import Enum
from functools import partial
from typing import Callable, List, Literal, Optional, Union

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC  # NOQA
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver

from lox_services.utils.general_python import print_error, print_success


def get_value_or_empty_string(
    driver: webdriver.Chrome, selector_type: By, selector: str
):
    """
    Retrieve the inner text of an HTML element specified by the given selector.

    Parameters:
        driver (webdriver.Chrome): The Chrome web driver used to interact with the web page.
        selector_type (By): The type of selector used to locate the HTML element.
                            It can be one of the By constants defined in the Selenium library.
        selector (str): The selector string used to identify the HTML element.

    Returns:
        str: The inner text of the specified HTML element if found, or an empty string if not found.
    """
    try:
        return driver.find_element(selector_type, selector).get_attribute("innerText")
    except NoSuchElementException:
        return ""


def wait_until_page_loaded(driver: webdriver.Chrome, timeout: int = 10):
    """Wait for webpage to completely load.
    ## Arguments:
    - `driver`: The driver that will be used to look at webpage.
    - `timeout`: The maximum number of seconds to wait until the function returns a timeout.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        return
    except TimeoutException as timeout_exception:
        raise TimeoutException from timeout_exception


def wait_for_end_of_download(folder_path: str, max_timeout=15):
    """Wait for downloads to finish with a max timeout.
    ## Arguments:
    - `folder_path`: The path to the folder where the files will be downloaded.
    - `max_timeout`: The maximum number of seconds to wait until timing out.

    ## Returns:
    The number of seconds that the download took.
    """
    if os.path.exists(folder_path):
        seconds = 0
        max_number_of_partial_downloads = 0
        is_downloaded = False
        print("Waiting for file to be downloaded...")
        while (not is_downloaded) and (seconds < max_timeout):
            time.sleep(1)
            seconds += 1
            number_of_partial_downloads = 0
            files = os.listdir(folder_path)
            for file in files:
                if file.endswith(".crdownload"):
                    number_of_partial_downloads += 1

            if number_of_partial_downloads > max_number_of_partial_downloads:
                max_number_of_partial_downloads = number_of_partial_downloads
            elif number_of_partial_downloads <= max_number_of_partial_downloads:
                is_downloaded = True
                print_success(f"File took {seconds}secs to download")
            else:
                print(f"{seconds}/{max_timeout} - Still downloading ...")

        return seconds


def safe_find_element(
    driver: webdriver.Chrome,
    *,
    selector_type: By = By.CSS_SELECTOR,
    selector: Union[str, Enum],
    timeout: int = 10,
    wait: Optional[WebDriverWait] = None,
) -> WebElement:
    """Find 1 element in the given driver.
    ## Arguments:
    - `driver`: The driver that will be used to look up the element.
    - `selector_type`: The type of the selector used (CSS by default). It can be any element of
    the selenium.webdriver.common.by.By .
    - `selector`: The selector used to look for the element.
    - `timeout`: The maximum number of seconds to wait until the function returns a timeout.
    - 'wait': a WebDriverWait instance to avoid repeated instance creation

    ## Returns:
    - The element that matches the selector.
    ## Raises
    - NoSuchElementException, TimeoutException if no element found within timeout.
    """
    if isinstance(selector, Enum):
        selector = selector.value
    if wait is None:
        wait = WebDriverWait(driver, timeout)
    element_present = EC.presence_of_element_located((selector_type, selector))
    return wait.until(element_present)


def find(
    driver: webdriver.Chrome,
    selector: Union[str, Enum],
    selector_type: By = By.CSS_SELECTOR,
) -> WebElement:
    """
    Same as 'safe_find_element', but without waiting. find(Some.CONSTANT) should be
    less typing than driver.find_element(Some.CONSTANT.value), which results in cleaner code.

    ## Arguments:
    - `driver`: The driver that will be used to look up the element.
    - `selector_type`: The type of the selector used (CSS by default). It can be any element of
    the selenium.webdriver.common.by.By .
    - `selector`: The selector used to look for the element.

    ## Returns:
    - The element that matches the selector.
    ## Raises
    - NoSuchElementException, TimeoutException if no element found within timeout.
    """

    if isinstance(selector, Enum):
        selector = selector.value
    return driver.find_element(selector_type, selector)


def safe_find_elements(
    driver: webdriver.Chrome,
    *,
    selector_type: By = By.CSS_SELECTOR,
    selector: str,
    timeout: int = 10,
) -> List[WebElement]:
    """Find all element matching the selector in the given driver.
    ## Arguments:
    - `driver`: The driver that will be used to look up for elements.
    - `selector_type`: The type of the selector used (CSS by default). It can be any element of
    the selenium.webdriver.common.by.By .
    - `selector`: The selector used to look for the elements.
    - `timeout`: The maximum number of seconds to wait until the function returns a timeout.

    ## Returns:
    - The elements that matches the selector.
    - NoSuchElementException if no element found within timeout.
    """
    try:
        element_present = EC.presence_of_element_located((selector_type, selector))
        WebDriverWait(driver, timeout).until(element_present)
        return driver.find_elements(selector_type, selector)
    except TimeoutException as timeout_exception:
        raise NoSuchElementException from timeout_exception
    except NoSuchElementException as no_such_element:
        raise NoSuchElementException from no_such_element
    except:
        print_error("An unknown error occurred in Utils.selenium.")
        raise


def wait_until_clickable_and_click(
    wait: Optional[WebDriverWait],
    selector: Union[str, Enum],
    timeout: int = 30,
    by: By = By.CSS_SELECTOR,
    driver: Optional[webdriver.Chrome] = None,
):
    """Wait until an element is clickable, then click on it using css selector.
    ## Arguments:
    - `wait`: The wait element that will be used to wait until a certain number of second.
    - `selector`: The selector used to look for the elements.
    - `timeout`: The maximum number of seconds to wait until the function returns a timeout.
    - 'by': select which element to look for
    - 'driver': The driver that can be used to create a WebDriverWait instance
    """
    if wait is None:
        wait = WebDriverWait(driver, timeout)
    if isinstance(selector, Enum):
        selector = selector.value
    element = wait.until(EC.element_to_be_clickable((by, selector)))
    element.click()


def wait_until_clickable_and_click_by_xpath(wait: WebDriverWait, selector: str):
    """Wait until an element is clickable, then click on it using xpath.
    ## Arguments:
    - `wait`: The wait element that will be used to wait until a certain number of second.
    - `selector`: The selector used to look for the elements.
    - `timeout`: The maximum number of seconds to wait until the function returns a timeout.
    """
    element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
    element.click()


def wait_then_clear(
    driver: webdriver.Chrome, wait: WebDriverWait, selector: str
) -> None:
    """Wait until an element appears, then clears it.
    ## Arguments:
        - `driver`: The driver that will be used to look up for elements.
        - `wait`: The wait element that will be used to wait until a certain number of second.
        - `selector`: The selector used to look for the elements.
    """
    wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, selector))
    driver.find_element(By.CSS_SELECTOR, selector).clear()


def wait_then_send_keys(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
    selector: str,
    input_text: str,
    clear: bool = False,
):
    """Wait until an element appears, then send keys to it.
    ## Arguments:
    - `driver`: The driver that will be used to look up for elements.
    - `wait`: The wait element that will be used to wait until a certain number of second.
    - `selector`: The selector used to look for the elements.
    - `input_text`: The text that will be sent to the element
    - `clear`: True if the field needs to be cleared before to get filled
    """
    wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, selector))
    if clear:
        driver.find_element(By.CSS_SELECTOR, selector).clear()
        time.sleep(0.3)

    driver.find_element(By.CSS_SELECTOR, selector).send_keys(input_text)


def safe_send_keys(
    driver: webdriver.Chrome,
    selector: str,
    input_text: str,
    selector_type: By = By.CSS_SELECTOR,
):
    """Sends keys with ActionChains to solve a Chrome version issue."""
    element = safe_find_element(driver, selector_type=selector_type, selector=selector)
    element.click()
    action = ActionChains(driver)
    action.send_keys(input_text)
    action.perform()


# Wait for the loading spinner to be gone
def wait_till_disapear(
    wait: WebDriverWait,
    selector_type: By = By.CSS_SELECTOR,
    selector: str = "",
    timeout: int = 60,
):
    """Wait until an element disappears
    ## Arguments:
    - `wait`: The wait element that will be used to wait until a certain number of second.
    - `selector_type`: The type of the selector used (CSS by default). It can be any element of
    the selenium.webdriver.common.by.By .
    - `selector`: The selector used to look for the elements.
    - `timeout`: The maximum number of seconds to wait until the function returns a timeout.
    """
    wait.until(EC.invisibility_of_element_located((selector_type, selector)))


def random_speed(average: float, threshold: float) -> float:
    """Generates a random value in the interval [ average-threshold ; average+threshold ].
    ## Arguments
    - `average`: The middle of the possible interval.
    - `threshold`: The max and min distance from the average.

    ## Returns
    - The random value.
    """
    if average < threshold:
        average = threshold
    return round(random.uniform(average - threshold, average + threshold), 3)


class JamesBond:
    def __init__(self):
        self.clicking_speed = round(random.uniform(2, 4), 2)
        self.typing_speed = round(
            random.uniform(self.clicking_speed / 2, self.clicking_speed), 2
        )
        print(f"James average clicking time: {self.clicking_speed} sec.")
        print(f"James average typing time: {self.typing_speed} sec.")

    def click(self):
        sleep_time = random_speed(self.clicking_speed, 0.5)
        # print(sleep_time)
        time.sleep(sleep_time)

    def type(self):
        sleep_time = random_speed(self.typing_speed, 0.2)
        # print(sleep_time)
        time.sleep(sleep_time)


def clear_local_storage(driver: webdriver.Chrome):
    driver.execute_script("window.localStorage.clear();")


DriverStorageType = Literal["cookies", "local", "session", "all"]


def clear_storage(driver: webdriver.Chrome, storage_type: DriverStorageType = "all"):
    if storage_type in ["cookies", "all"]:
        driver.delete_all_cookies()
    if storage_type in ["local", "all"]:
        driver.execute_script("window.localStorage.clear();")
    if storage_type in ["session", "all"]:
        driver.execute_script("window.sessionStorage.clear();")


def bind_arguments_to_a_selenium_func(
    func: Callable,
    driver: webdriver.Chrome,
    wait: Optional[WebDriverWait] = None,
    default_type: Optional[By] = None,
) -> Callable:
    """Declutter repeated calls to some designated Selenium function by binding a
    specific WebDriver, WebDriverWait and By instances as default arguments to it."""

    partial_func = (
        partial(func, driver=driver, wait=wait)
        if wait is not None
        else partial(func, driver=driver)
    )
    if default_type is None:
        return partial_func
    return partial(partial_func, selector_type=default_type)
