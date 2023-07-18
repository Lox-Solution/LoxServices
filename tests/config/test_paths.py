import unittest
import os
from lox_services.config.paths import (
    ROOT_PATH,
    CLOUD_ROOT_PATH,
    OUTPUT_FOLDER,
    CHROMEDRIVER_PATH,
)


class TestConfiguration(unittest.TestCase):
    def test_root_path(self):
        # Assert that ROOT_PATH is not empty
        self.assertIsNotNone(ROOT_PATH)
        # Assert that ROOT_PATH is a string
        self.assertIsInstance(ROOT_PATH, str)

    def test_cloud_root_path(self):
        # Assert that CLOUD_ROOT_PATH is not empty
        self.assertIsNotNone(CLOUD_ROOT_PATH)
        # Assert that CLOUD_ROOT_PATH is a string
        self.assertIsInstance(CLOUD_ROOT_PATH, str)

    def test_output_folder(self):
        # Assert that OUTPUT_FOLDER is not empty
        self.assertIsNotNone(OUTPUT_FOLDER)
        # Assert that OUTPUT_FOLDER is a string
        self.assertIsInstance(OUTPUT_FOLDER, str)

    def test_chromedriver_path(self):
        # Assert that CHROMEDRIVER_PATH is not empty
        self.assertIsNotNone(CHROMEDRIVER_PATH)
        # Assert that CHROMEDRIVER_PATH is a string
        self.assertIsInstance(CHROMEDRIVER_PATH, str)


if __name__ == "__main__":
    unittest.main()
