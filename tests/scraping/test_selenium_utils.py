import os
import shutil
import time
import unittest
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from lox_services.scraping.chromedriver import run_chromedriver
import undetected_chromedriver as uc
from lox_services.scraping.selenium_util import (
    wait_until_page_loaded,
    wait_for_end_of_download,
    safe_find_element,
    find,
    safe_find_elements,
    wait_until_clickable_and_click,
    wait_until_clickable_and_click_by_xpath,
    wait_then_clear,
    wait_then_send_keys,
    safe_send_keys,
    wait_till_disapear,
    clear_local_storage,
    clear_storage,
    bind_arguments_to_a_selenium_func,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import ui
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from lox_services.utils.decorators import VirtualDisplay
from mock import patch

from tests import OUTPUT_FOLDER

DEFAULT_TIMEOUT = 5
DEFAULT_WRONG_CSS_SELECTOR = ".wrong_selector"
DEFAULT_RIGHT_CSS_SELECTOR = "#fname"
POPUP_BUTTON = "#qc-cmp2-ui div > button:nth-child(2)"
DEFAULT_SELECTOR_TYPE = By.CSS_SELECTOR
DEFAULT_TEXT_TO_WRITE = "some text"


class TestUtils(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            "ENVIRONMENT": "production",
        },
    )
    @VirtualDisplay
    def setUp(self):
        self.folder_path = os.path.join(
            OUTPUT_FOLDER, "tests", "scraping", "download_folder"
        )
        os.makedirs(self.folder_path, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.folder_path):
            shutil.rmtree(self.folder_path)

    def ups_clear_cookie_banner(self, driver, wait):
        wait_until_page_loaded(driver)
        # Clear the cookie banner
        wait_until_clickable_and_click(
            wait,
            "#__tealiumGDPRecModal > div.privacy_prompt_middle > div > div.privacy_prompt_content > div.option_set > div:nth-child(1) > label",
            DEFAULT_TIMEOUT,
            DEFAULT_SELECTOR_TYPE,
        )
        wait_until_clickable_and_click(
            wait, "#consent_prompt_submit", DEFAULT_TIMEOUT, DEFAULT_SELECTOR_TYPE
        )
        time.sleep(0.5)

    def test_wait_until_page_loaded(self):
        # Set the environment variable before calling the decorator

        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")

            wait_until_page_loaded(driver=driver)
            self.assertTrue(True)

        inner_test_method(self)

    # def test_wait_for_end_of_download(self):
    #     # Test case for successful download completion
    #     downloaded_file = os.path.join(self.folder_path, "temp_file.csv")
    #     with open(downloaded_file, "w") as f:
    #         f.write("Download,Completed")
    #     seconds = wait_for_end_of_download(self.folder_path, DEFAULT_TIMEOUT)

    #     self.assertLess(seconds, DEFAULT_TIMEOUT)

    #     # Test case for download not completed within timeout
    #     partially_downloaded_file = os.path.join(
    #         self.folder_path, "temp_file.crdownload"
    #     )
    #     with open(partially_downloaded_file, "w") as f:
    #         f.write("Download,Not,Completed")

    #     seconds = wait_for_end_of_download(self.folder_path, DEFAULT_TIMEOUT)

    #     self.assertEqual(seconds, DEFAULT_TIMEOUT)

    def test_safe_find_element(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")

            wait = WebDriverWait(driver, 15)

            element = safe_find_element(
                driver=driver,
                selector_type=DEFAULT_SELECTOR_TYPE,
                selector=DEFAULT_RIGHT_CSS_SELECTOR,
                wait=wait,
                timeout=DEFAULT_TIMEOUT,
            )
            self.assertIsInstance(element, WebElement)

            with self.assertRaises(TimeoutException):
                safe_find_element(
                    driver=driver,
                    selector_type=DEFAULT_SELECTOR_TYPE,
                    selector=DEFAULT_WRONG_CSS_SELECTOR,
                    wait=wait,
                    timeout=DEFAULT_TIMEOUT,
                )

        inner_test_method(self)

    def test_find(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")

            element = find(driver, DEFAULT_RIGHT_CSS_SELECTOR, DEFAULT_SELECTOR_TYPE)
            self.assertIsInstance(element, WebElement)

            with self.assertRaises(NoSuchElementException):
                find(driver, DEFAULT_WRONG_CSS_SELECTOR, DEFAULT_SELECTOR_TYPE)

        inner_test_method(self)

    def test_safe_find_elements(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")

            elements = safe_find_elements(
                driver=driver,
                selector_type=DEFAULT_SELECTOR_TYPE,
                selector="#commonWebElements > form",
                timeout=DEFAULT_TIMEOUT,
            )
            self.assertEqual(len(elements), 2)

            with self.assertRaises(NoSuchElementException):
                safe_find_elements(
                    driver=driver,
                    selector_type=DEFAULT_SELECTOR_TYPE,
                    selector=DEFAULT_WRONG_CSS_SELECTOR,
                    timeout=DEFAULT_TIMEOUT,
                )

        inner_test_method(self)

    def test_wait_until_clickable_and_click(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")

            wait = WebDriverWait(driver, 15)

            # Test case for successful click with wait
            wait_until_clickable_and_click(
                wait,
                DEFAULT_RIGHT_CSS_SELECTOR,
                DEFAULT_TIMEOUT,
                DEFAULT_SELECTOR_TYPE,
            )

            # If the function completes without raising an exception, it executed well
            self.assertTrue(True)

            # Test case for successful click with driver
            wait_until_clickable_and_click(
                None,
                DEFAULT_RIGHT_CSS_SELECTOR,
                DEFAULT_TIMEOUT,
                DEFAULT_SELECTOR_TYPE,
                driver,
            )

            # If the function completes without raising an exception, it executed well
            self.assertTrue(True)

            # Test case for click on non-clickable element and wait
            with self.assertRaises(TimeoutException):
                wait_until_clickable_and_click(
                    wait,
                    DEFAULT_WRONG_CSS_SELECTOR,
                    DEFAULT_TIMEOUT,
                    DEFAULT_SELECTOR_TYPE,
                )

            # Test case for click on non-clickable element and driver
            with self.assertRaises(TimeoutException):
                wait_until_clickable_and_click(
                    None,
                    DEFAULT_WRONG_CSS_SELECTOR,
                    DEFAULT_TIMEOUT,
                    DEFAULT_SELECTOR_TYPE,
                    driver,
                )

        inner_test_method(self)

    def test_wait_until_clickable_and_click_by_xpath(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")

            wait = WebDriverWait(driver, 15)

            # Test case for successful click by XPath
            xpath = '//*[@id="idOfButton"]'
            wait_until_clickable_and_click_by_xpath(wait, xpath)

            # Test case for click on non-clickable element by XPath
            wrong_xpath = '//button[@id="wrongId"]'
            with self.assertRaises(TimeoutException):
                wait_until_clickable_and_click_by_xpath(wait, wrong_xpath)

        inner_test_method(self)

    def test_wait_then_clear(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")

            wait = WebDriverWait(driver, 15)

            safe_send_keys(
                driver,
                DEFAULT_RIGHT_CSS_SELECTOR,
                DEFAULT_TEXT_TO_WRITE,
                selector_type=By.CSS_SELECTOR,
            )

            # Assert that the input is not empty before calling wait_then_clear
            element = safe_find_element(
                driver=driver,
                selector_type=DEFAULT_SELECTOR_TYPE,
                selector=DEFAULT_RIGHT_CSS_SELECTOR,
                wait=wait,
                timeout=DEFAULT_TIMEOUT,
            )

            value_before_clear = element.get_attribute("value")
            self.assertEqual(value_before_clear, DEFAULT_TEXT_TO_WRITE)

            # Call wait_then_clear and assert that the input is cleared
            wait_then_clear(driver, wait, DEFAULT_RIGHT_CSS_SELECTOR)
            value_after_clear = element.get_attribute("value")
            self.assertEqual(value_after_clear, "")

            # Test case when the element doesn't exist
            with self.assertRaises(TimeoutException):
                wait_then_clear(driver, wait, DEFAULT_WRONG_CSS_SELECTOR)

        inner_test_method(self)

    def test_wait_then_send_keys(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            wait = WebDriverWait(driver, 15)

            driver.get(
                "https://wwwapps.ups.com/doapp/signup?loc=nl_NL&ClientId=13&returnto=https:%2F%2Fwww.ups.com%2Fnl%2Fnl%2FHome.page"
            )
            self.ups_clear_cookie_banner(driver, wait)
            # Test case when the element exists
            wait_then_send_keys(
                driver, wait, "#signUpName", DEFAULT_TEXT_TO_WRITE, clear=True
            )

            # Perform assertions to check if the input was successfully sent
            element = driver.find_element(By.CSS_SELECTOR, "#signUpName")
            value = element.get_attribute("value")
            self.assertEqual(value, DEFAULT_TEXT_TO_WRITE)

            # Test case when the element exists and the clear is not applied
            wait_then_send_keys(
                driver,
                wait,
                "#signUpName",
                DEFAULT_TEXT_TO_WRITE,
                clear=False,
            )

            # Perform assertions to check if the input was successfully sent without clearing
            element = driver.find_element(By.CSS_SELECTOR, "#signUpName")
            value = element.get_attribute("value")
            self.assertEqual(value, DEFAULT_TEXT_TO_WRITE + DEFAULT_TEXT_TO_WRITE)

            # Test case when the element exists and the clear is applied
            wait_then_send_keys(
                driver, wait, "#signUpName", DEFAULT_TEXT_TO_WRITE, clear=True
            )

            # Perform assertions to check if the input was successfully sent with clearing
            element = driver.find_element(By.CSS_SELECTOR, "#signUpName")
            value = element.get_attribute("value")
            self.assertEqual(value, DEFAULT_TEXT_TO_WRITE)

            # Test case when the element doesn't exist
            with self.assertRaises(TimeoutException):
                wait_then_send_keys(
                    driver=driver,
                    wait=wait,
                    selector=DEFAULT_WRONG_CSS_SELECTOR,
                    input_text=DEFAULT_TEXT_TO_WRITE,
                )

        inner_test_method(self)

    def test_safe_send_keys(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")

            wait = WebDriverWait(driver, 15)

            self.clear_cookie_banner(driver, wait)

            # Test case when the element exists
            safe_send_keys(
                driver,
                DEFAULT_RIGHT_CSS_SELECTOR,
                DEFAULT_TEXT_TO_WRITE,
                selector_type=By.CSS_SELECTOR,
            )

            # Perform assertions to check if the input was successfully sent
            element = driver.find_element(By.CSS_SELECTOR, DEFAULT_RIGHT_CSS_SELECTOR)
            value = element.get_attribute("value")
            self.assertEqual(value, DEFAULT_TEXT_TO_WRITE)

            # Test case when the element doesn't exist
            with self.assertRaises(TimeoutException):
                safe_send_keys(
                    driver,
                    DEFAULT_WRONG_CSS_SELECTOR,
                    DEFAULT_TEXT_TO_WRITE,
                    selector_type=By.CSS_SELECTOR,
                )

        inner_test_method(self)

    def test_wait_till_disapear(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )

            wait = WebDriverWait(driver, 15)

            driver.get(
                "https://wwwapps.ups.com/doapp/signup?loc=nl_NL&ClientId=13&returnto=https:%2F%2Fwww.ups.com%2Fnl%2Fnl%2FHome.page"
            )
            self.ups_clear_cookie_banner(driver, wait)

            wait_till_disapear(
                wait=wait,
                selector_type=DEFAULT_SELECTOR_TYPE,
                selector="div > div > img",
                timeout=DEFAULT_TIMEOUT,
            )
            self.assertTrue(True)

        inner_test_method(self)

    def test_clear_local_storage(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")

            driver.execute_script("localStorage.setItem('item1', 'value1');")
            driver.execute_script("localStorage.setItem('item2', 'value2');")
            # Test if the we managed to add items to the local storage
            self.assertGreater(driver.execute_script("return localStorage.length;"), 2)
            clear_local_storage(driver)
            # Test if the local storage is empty
            self.assertEqual(driver.execute_script("return localStorage.length;"), 0)

        inner_test_method(self)

    def test_clear_storage(self):
        @patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        )
        @VirtualDisplay
        def inner_test_method(self):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://artoftesting.com/samplesiteforselenium")
            # Test case for clearing cookies
            driver.add_cookie({"name": "cookie1", "value": "value1"})
            driver.add_cookie({"name": "cookie2", "value": "value2"})
            self.assertGreaterEqual(len(driver.get_cookies()), 2)
            clear_storage(driver, storage_type="cookies")
            self.assertEqual(len(driver.get_cookies()), 0)

            # Test case for clearing local storage
            driver.execute_script("window.localStorage.setItem('item1', 'value1');")
            driver.execute_script("window.localStorage.setItem('item2', 'value2');")
            self.assertGreaterEqual(
                driver.execute_script("return window.localStorage.length;"), 2
            )
            clear_storage(driver, storage_type="local")
            self.assertEqual(
                driver.execute_script("return window.localStorage.length;"), 0
            )

            # Test case for clearing session storage
            driver.execute_script("window.sessionStorage.setItem('item1', 'value1');")
            driver.execute_script("window.sessionStorage.setItem('item2', 'value2');")
            self.assertGreaterEqual(
                driver.execute_script("return window.sessionStorage.length;"), 2
            )
            clear_storage(driver, storage_type="session")
            self.assertEqual(
                driver.execute_script("return window.sessionStorage.length;"), 0
            )

            # Test case for clearing all storage
            driver.add_cookie({"name": "cookie1", "value": "value1"})
            driver.execute_script("window.localStorage.setItem('item1', 'value1');")
            driver.execute_script("window.sessionStorage.setItem('item2', 'value2');")

            cookies = driver.get_cookies()
            self.assertGreaterEqual(len(cookies), 1)
            self.assertGreaterEqual(
                driver.execute_script("return window.localStorage.length;"), 1
            )
            self.assertGreaterEqual(
                driver.execute_script("return window.sessionStorage.length;"), 1
            )

        inner_test_method(self)

    def test_bind_arguments_to_a_selenium_func(self):
        # TODO
        return


if __name__ == "__main__":
    unittest.main()
