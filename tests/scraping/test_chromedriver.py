import os
import time
import shutil
import unittest

from selenium.webdriver.common.by import By
from lox_services.scraping.chromedriver import (
    run_chromedriver,
)
from selenium.webdriver.support.ui import WebDriverWait
from lox_services.scraping.selenium_util import (
    wait_for_end_of_download,
    wait_until_clickable_and_click,
)
from selenium.common.exceptions import WebDriverException
from lox_services.utils.decorators import VirtualDisplay
from tests import OUTPUT_FOLDER
import undetected_chromedriver as undetected_webdriver
from mock import patch


class TestChromeDriver(unittest.TestCase):
    def setUp(self):
        self.folder_path = os.path.join(
            OUTPUT_FOLDER, "tests", "scraping", "download_folder"
        )
        os.makedirs(self.folder_path, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.folder_path):
            shutil.rmtree(self.folder_path)

    @VirtualDisplay
    def test_run_chromedriver(self):
        driver = run_chromedriver(
            download_folder=self.folder_path,
            size_length=960,
            size_width=960,
        )

        wait = WebDriverWait(driver, 15)

        driver.get("https://fastest.fish/test-files")

        # Check that no file was downloaded
        self.assertEqual(
            sum(len(files) for _, _, files in os.walk(self.folder_path)), 0
        )

        time.sleep(1)
        # Download a very small file
        wait_until_clickable_and_click(
            wait=wait,
            selector="#vue > table > tbody > tr:nth-child(1) > td:nth-child(1) > a",
            timeout=15,
            by=By.CSS_SELECTOR,
        )
        wait_for_end_of_download(self.folder_path, 15)

        # Check that one file was downloaded
        self.assertEqual(
            sum(len(files) for _, _, files in os.walk(self.folder_path)), 1
        )

    @VirtualDisplay
    def test_run_chromedriver_prodiction(self):
        # Test that the first driver is closed when a second one is created
        driver1 = run_chromedriver(
            download_folder=self.folder_path,
            size_length=960,
            size_width=960,
        )

        with patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        ):
            driver2 = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )

        # It is not possible to access the driver after it has been closed
        with self.assertRaises(Exception):
            driver1.get("https://fastest.fish/test-files")

        driver2.get("https://fastest.fish/test-files")
        self.assertIsInstance(driver2, undetected_webdriver.Chrome)

    @VirtualDisplay
    def test_chromedriver_screenshot(self):
        with patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
            },
        ):
            driver = run_chromedriver(
                download_folder=self.folder_path,
                size_length=960,
                size_width=960,
            )
            driver.get("https://fastest.fish/test-files")

            wait = WebDriverWait(driver, 5)

            with self.assertRaises(WebDriverException):
                wait_until_clickable_and_click(wait, "wrong_selector", 5)


if __name__ == "__main__":
    unittest.main()
