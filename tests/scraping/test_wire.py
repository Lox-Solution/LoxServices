import unittest
import seleniumwire.undetected_chromedriver as uc
from lox_services.scraping.wire import run_simple_chromedriver


class TestRunSimpleChromedriver(unittest.TestCase):
    def test_run_simple_chromedriver_returns_instance(self):
        # Arrange

        # Act
        driver = run_simple_chromedriver()

        # Assert
        self.assertIsNotNone(driver)
        self.assertIsInstance(driver, uc.Chrome)


if __name__ == "__main__":
    unittest.main()
