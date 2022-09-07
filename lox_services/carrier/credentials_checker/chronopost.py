from typing import Dict
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from xvfbwrapper import Xvfb

from lox_services.carrier.classes import CredentialsChecker, WrongCredentialsException
from lox_services.carrier.constants import CHROME_OPTIONS
from lox_services.config.paths import CHROMEDRIVER_PATH

from lox_services.scraping.selenium_util import safe_find_element, safe_send_keys
from lox_services.utils.decorators import Perf

CARRIER = "Chronopost"

class ChronopostCredentialsChecker(CredentialsChecker):
    """Check credentials for Chronopost"""
    
    @Perf
    def check_credentials(self, credentials):
        """Useses Selenium and Xvfb to check credentials."""
        try:
            self.__login(credentials)
        except WrongCredentialsException:
            return False
        
        return True
    
    def get_average_compute_time(self):
        return 10
    
    def __login(self, credentials):
        """Connects a driver to Chronopost website (www.chronopost.fr)."""
        print("Connecting to Chronopost website ...")
        company = credentials["company"]
        username = credentials['username']
        password = credentials['password']
        driver = Chrome(
            service=Service(executable_path=CHROMEDRIVER_PATH),
            options=CHROME_OPTIONS
        )
        with driver:
            driver.get("https://www.chronopost.fr/en#/step-home")
            
            # if already connected
            if len(driver.find_elements(By.CSS_SELECTOR, '#block-chrono-angular-js-inclusion-connection-js-block > div > div > ul > li > a')) > 0:
                driver.find_element(By.CSS_SELECTOR, '#block-chrono-angular-js-inclusion-connection-js-block > div > div > ul > li > a').click()
            
            # Accepts cookies
            try:
                safe_find_element(driver, selector='#c-right > a:nth-child(1)', timeout=3).click()
                print("Cookies accepted.")
            except Exception:
                print("No cookie window found.")
                
            # Tries to connect
            connection_div = "#block-chrono-angular-js-inclusion-connection-js-block > div > span > div"
            safe_send_keys(driver, f'{connection_div} > div.form-type-textfield.form-item-name.form-item.form-group > input', username)
            safe_send_keys(driver, f'{connection_div} > div.form-type-password.form-item-pass.form-item.form-group > input', password)
            safe_find_element(driver, selector=f'{connection_div} > button').click()
            
            # Check if connected
            try:
                safe_find_element(driver, selector=".alert.alert-block.alert-danger", timeout=2)
                raise WrongCredentialsException()
            except NoSuchElementException:
                print(f"Connected as {username} ({company}).")
                return


class ChronotraceCredentialsChecker(CredentialsChecker):
    """Check credentials for Chronopost"""
    
    @Perf
    def check_credentials(self, credentials):
        xvfb = Xvfb(width=1280, height=1024, colordepth=16)
        with xvfb:
            try:
                self.__login(credentials)
            except WrongCredentialsException:
                return False
            
            return True
    
    def get_average_compute_time(self):
        return 3
    
    def __login(self, credentials: Dict):
        """Connects a driver to Chronotrace website (www.chronotrace.chronopost.com)."""
        print("Connecting to Chronopost chronotrace website ...")
        company = credentials["company"]
        username = credentials['username']
        password = credentials['password']
        
        driver = Chrome(service=Service(executable_path=CHROMEDRIVER_PATH))
        with driver:
            driver.get("https://www.chronotrace.chronopost.com/chronotraceV3/welcomePage.do")
            
            safe_send_keys(driver, "#iden", username)
            safe_send_keys(driver, "#mdpa", password)
            safe_find_element(driver, selector="#submitBoutton").click()
            
            # Check if connected
            try:
                safe_find_element(driver, selector="form > .error", timeout=1)
                raise WrongCredentialsException()
            
            except NoSuchElementException:
                print(f"Connected as {username} ({company}).")
                return None


if __name__ == "__main__":
    test_credentials = {
        "company": "Bergamotte",
        "username": "reclamations@bergamotte.com",
        "password": "password goes here"
    }
    chronotrace = ChronopostCredentialsChecker()
    is_valid_credential = chronotrace.check_credentials(test_credentials)
    print(is_valid_credential)
