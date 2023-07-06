import os
import time
import shutil
import unittest

from selenium.webdriver.common.by import By
from lox_services.scraping.chromedriver import run_chromedriver
from selenium.webdriver.support.ui import WebDriverWait
from lox_services.scraping.selenium_util import (
    wait_for_end_of_download,
    wait_until_clickable_and_click,
)


class TestChromeDriver(unittest.TestCase):
    def setUp(self):
        self.folder_path = os.path.join(
            os.getcwd(), "tests", "scraping", "download_folder"
        )
        os.makedirs(self.folder_path, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.folder_path):
            shutil.rmtree(self.folder_path)

    def test_run_chromedriver(self):
        # Mock the return value of init_chromedriver

        # Test case 1: chromedriver is running
        driver = run_chromedriver(
            download_folder=self.folder_path,
            size_length=960,
            size_width=960,
        )

        wait = WebDriverWait(driver, 15)

        # If the chromedriver is running, then the function is working
        self.assertTrue(True)

        # Test case 2: chromedriver is downloading the file at the given folder path
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

        # Check that 1 file was downloaded
        self.assertEqual(
            sum(len(files) for _, _, files in os.walk(self.folder_path)), 1
        )


if __name__ == "__main__":
    unittest.main()
