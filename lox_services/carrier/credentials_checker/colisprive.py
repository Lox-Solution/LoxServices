from typing import Dict

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from xvfbwrapper import Xvfb

from lox_services.carrier.classes import CredentialsChecker, WrongCredentialsException
from lox_services.config.paths import CHROMEDRIVER_PATH
from lox_services.scraping.selenium_util import safe_find_element
from lox_services.utils.decorators import Perf


class ColispriveCredentialsChecker(CredentialsChecker):
    """Check credentials for Colisprive"""
    
    @Perf
    def check_credentials(self, credentials):
        """Useses Selenium and Xvfb to check credentials."""
        xvfb = Xvfb(width=1280, height=1024, colordepth=16)
        with xvfb:
            try:
                self.__login(credentials)
            except WrongCredentialsException:
                return False
            
            return True
    
    def get_average_compute_time(self):
        return 5
    
    def __login(self, credentials: Dict):
        """Connects a driver to Colisprive"""
        print("Connecting to Colisprive website ...")
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
            # driver.get('https://www.colisprive.fr')
            # time.sleep(5)
            driver.get('https://www.colisprive.com/agence/Account/Login.aspx?ReturnUrl=%2fAgence%2f')

            user_input = safe_find_element(
                driver,
                selector='#LM_RM_RS_Ct_MCt_tbUserName_I'
            )
            user_input.click()
            user_input.send_keys(username)
            print("Username entered")

            password_input = safe_find_element(
                driver,
                selector='#LM_RM_RS_Ct_MCt_tbPassword_I'
            )
            password_input.click()
            password_input.send_keys(password)
            print("Password entered")
            
            submit = safe_find_element(
                driver,
                selector='#LM_RM_RS_Ct_MCt_btnLogin_CD > span'
            )
            submit.click()
            print("Submit clicked")
            
            try: 
                safe_find_element(
                    driver,
                    selector='#LM_RM_RS_Ct_MCt_tbUserName_EC',
                    timeout=3
                ) # error displayed if wrong credentials
                raise WrongCredentialsException()
            except NoSuchElementException:
                print(f"Connected as {username} ({company}).")
        
        return

if __name__ == "__main__":
    test_credentials = {
        "company": "Teezily",
        "username": "TEEZILY",
        "password": "Password goes here"
    }
    colisprive = ColispriveCredentialsChecker()
    is_valid_credential = colisprive.check_credentials(test_credentials)
    print(is_valid_credential)
