"""Undetected chrome driver class with configuration."""
import os
import time
from sys import platform
from selenium import webdriver
# from selenium.webdriver.common.by import By

import undetected_chromedriver.v2 as undetected_chromedriver

from lox_services.scraping.selenium_util import safe_find_element
from lox_services.config.paths import ROOT_PATH


class UndetectedChromeDriver(undetected_chromedriver.Chrome):
    """UndetectedChromeDriver with basic options for Lox usage."""
    
    def __init__(self, *args, company: str, **kwargs):
        options = undetected_chromedriver.ChromeOptions()
        print("Company: %s" % company)
        username = os.getlogin()
        if platform in ["linux", "linux2"]: # Linux (Ubuntu)
            # user_data_dir = "/tmp/profile"
            # user_data_dir = f"/home/{username}/.config/google-chrome/"
            user_data_dir = os.path.join(ROOT_PATH, "Selenium", ".config", "chrome")
            # profile_directory = "Profile 1"

        elif platform in ["darwin"]: # OS X (Macintosh)
            user_data_dir = f"/Users/{username}/Library/Application Support/Google/Chrome/"
            # profile_directory = "Default"
        
        else:
            print("Platform:", platform)
            raise Exception("UndetectedChromeDriver exception. Unable to setup with current platform.")

        options.user_data_dir = user_data_dir
        options.add_argument('--no-first-run')
        options.add_argument('--no-service-autorun')
        options.add_argument('--password-store=basic')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--start-maximized')
        # options.add_argument(f'--profile-directory={profile_directory}')
            
        kwargs["options"] = options
        print("kwargs: ",kwargs)
        super().__init__(*args, **kwargs)

def log_in_google_account(target_driver: webdriver.Chrome, username: str, password: str):
    url = 'https://www.google.com/accounts/Login'
    target_driver.get(url)
    if 'myaccount.google.com' in target_driver.current_url:
        print("Already logged in.")
        driver.get("https://www.google.com/")
        return
    
    print("Logging in with account: ", username)
    safe_find_element(target_driver, selector="#identifierId").send_keys(username)
    safe_find_element(target_driver, selector="#identifierNext").click()
    password_input = safe_find_element(target_driver, selector="#password > div > div > div > input")
    password_input.click()
    password_input.send_keys(password)
    safe_find_element(target_driver, selector="#passwordNext").click()
    time.sleep(2)
    driver.get("https://www.google.com/")
    print("Logged in.")

