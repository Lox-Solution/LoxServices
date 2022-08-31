import time
from typing import Dict
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from xvfbwrapper import Xvfb

from lox_services.carrier.classes import CredentialsChecker, WrongCredentialsException
from lox_services.config.paths import CHROMEDRIVER_PATH

from lox_services.scraping.selenium_util import safe_find_element
from lox_services.utils.decorators import Perf

CARRIER = "UPS"

class UPSCredentialsChecker(CredentialsChecker):
    """Check credentials for Chronopost"""
    
    @Perf
    def check_credentials(self, credentials):
        """Useses Selenium and Xvfb to check credentials."""
        # xvfb = Xvfb(width=1280, height=1024, colordepth=16)
        # with xvfb:
        try:
            self.__login(credentials)
        except WrongCredentialsException:
            return False
        
        return True
    
    def get_average_compute_time(self):
        return 10
    
    # def dodge_cloudflare(self, driver: Chrome, url: str):
    #     url_cloudfare = driver.current_url
    #     # Jump to a second tab and go to the same url ( should unlock the first one )
    #     driver.execute_script(f'window.open("{url}","_blank");')
    #     driver.switch_to.window(driver.window_handles[1])     
    #     driver.get(url_cloudfare)
    #     # Wait and come back to our original tab and paste the final url
    #     time.sleep(10)
    #     driver.close()
    #     driver.switch_to.window(driver.window_handles[0])
    #     driver.get(url)
    
    def __login(self, credentials: Dict):
        print("Connecting to UPS platform ...")
        company = credentials["company"]
        username = credentials['username']
        password = credentials['password']
        options = Options()
        options.add_argument("--start-maximized")
        driver = Chrome(
            service=Service(executable_path=CHROMEDRIVER_PATH),
            options=options
        )
        with driver:
            driver.get("https://www.ups.com/lasso/login")
            safe_find_element(driver, selector='#email', timeout=3).send_keys(username)
            safe_find_element(driver, selector='#pwd', timeout=3).send_keys(password)
            safe_find_element(driver, selector='button[name="getTokenWithPassword"]', timeout=3).click()
            time.sleep(30)
            try:
                safe_find_element(driver, selector=".alert.alert-block.alert-danger", timeout=2)
                raise WrongCredentialsException()
            except NoSuchElementException:
                print(f"Connected as {username} ({company}).")
                return


if __name__ == "__main__":
    test_credentials = {
        "company": "Suitsupply",
        "username": "ServiceInt2013",
        "password": "password goes here"
    }
    chronotrace = UPSCredentialsChecker()
    is_valid_credential = chronotrace.check_credentials(test_credentials)
    print(is_valid_credential)
