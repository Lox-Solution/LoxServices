import time
from typing import Dict
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from xvfbwrapper import Xvfb

from lox_services.carrier.classes import CredentialsChecker, WrongCredentialsException
from lox_services.carrier.constants import CHROME_OPTIONS
from lox_services.config.paths import CHROMEDRIVER_PATH

from lox_services.scraping.selenium_util import safe_find_element, safe_find_elements
from lox_services.utils.decorators import Perf

CARRIER = "Colissimo"

class ColissimoCredentialsChecker(CredentialsChecker):
    """Check credentials for Colissimo"""
    
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
        return 22
    
    def __login(self, credentials: Dict):
        """Connects a driver to Colissimo"""
        print("Connecting to Colissimo website ...")
        company = credentials["company"]
        username = credentials['username']
        password = credentials['password']
        driver = Chrome(
            service=Service(executable_path=CHROMEDRIVER_PATH),
            options=CHROME_OPTIONS
        )
        with driver:
            submit_button_selector = '#edit-connect'
            driver.get("https://www.colissimo.entreprise.laposte.fr")
            
            # Accept cookies
            try: 
                safe_find_elements(driver,selector='#popup-buttons > button')[1].click()
                print("Cookies accepted.")
            except Exception:
                pass
            
            # Welcome window
            try:
                safe_find_element(
                    driver,
                    selector='body > div.shepherd-has-cancel-icon.shepherd-has-title.shepherd-element.drupal-tour.shepherd-centered.shepherd-enabled > div > header > button'
                ).click()
                print("Welcome window quited.")
            except Exception:
                print("No welcome window.")
                pass

            safe_find_element(driver,selector='#block-userheaderblock').click()

            is_colissimo_fucked_up = True
            while is_colissimo_fucked_up:
                safe_find_element(driver,selector= "input#edit-login").clear()
                safe_find_element(driver,selector= "input#edit-login").send_keys(username)
                
                safe_find_element(driver,selector= "input#edit-pass").clear()
                safe_find_element(driver,selector= "input#edit-pass").send_keys(password)
                
                safe_find_element(driver,selector= submit_button_selector, timeout=5).click()
                time.sleep(3)
                try:
                    first_connection_error = safe_find_element(driver, selector= "div[role=alert]")
                    print("Connection alert:", first_connection_error.text)
                    if "An unrecoverable error occurred. The uploaded file likely exceeded the maximum file size (200 MB) that this server supports." in first_connection_error.text:
                        print("Trying to connect again ...")
                    
                    elif "La saisie de votre identifiant et/ou mot de passe est incorrecte." in first_connection_error.text:
                        raise WrongCredentialsException()
                    
                    else:
                        raise Exception("Unknown error occured" + first_connection_error.text)
                
                except NoSuchElementException:
                    is_colissimo_fucked_up = False
                    print("No connection alert.")
            
            print(f"Connected as {username} ({company}).")
        
        return



if __name__ == "__main__":
    test_credentials = {
        "company": "Jalontec",
        "username": "828071",
        "password": "password goes here"
    }
    colissimo = ColissimoCredentialsChecker()
    is_valid_credential = colissimo.check_credentials(test_credentials)
    print(is_valid_credential)
