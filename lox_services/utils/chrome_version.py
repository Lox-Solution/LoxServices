import os
import re
from sys import platform

from lox_services.utils.general_python import print_info

def extract_version_registry(output: str) -> str:
    """Extracts the version of Chrome from the registry output for Windows machines.

    Args:
        output (str): The output of the registry query.
    """
    try:
        google_version = ''
        for letter in output[output.rindex('DisplayVersion    REG_SZ') + 24:]:
            if letter != '\n':
                google_version += letter
            else:
                break
        return google_version.strip()
    except TypeError:
        return

def extract_version_folder() -> str:
    """Check if the Chrome folder exists in the x32 or x64 Program Files folders for Windows machines.

    Returns:
        str: The version of Chrome.
    """
    for i in range(2):
        path = 'C:\\Program Files' + (' (x86)' if i else '') +'\\Google\\Chrome\\Application'
        if os.path.isdir(path):
            paths = [f.path for f in os.scandir(path) if f.is_dir()]
            for path in paths:
                filename = os.path.basename(path)
                pattern = '\d+\.\d+\.\d+\.\d+'
                match = re.search(pattern, filename)
                if match and match.group():
                    # Found a Chrome version.
                    return match.group(0)
    return None


def get_chrome_version(fallback_version: int = 114) -> int:
    """Get the version of Chrome installed on the machine.

    Args:
        fallback_version (int): The version to return, if the chrome version is not found by script. Defaults to 109.

    Returns:
        int: The version of Chrome. If version is not found, return fallback_version.
    """
    version = None
    install_path = None

    try:
        if platform == "linux" or platform == "linux2":
            # linux
            install_path = "/usr/bin/chromium-browser"
        elif platform == "darwin":
            # OS X
            install_path = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
        elif platform == "win32":
            # Windows...
            try:
                # Try registry key.
                stream = os.popen('reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome"')
                output = stream.read()
                version = extract_version_registry(output)
            except Exception as ex:
                # Try folder path.
                version = extract_version_folder()
    except Exception as ex:
        print_info(f"Error while getting Chrome version: {ex}, returning deault version {fallback_version}.")
        
    full_version = os.popen(f"{install_path} --version").read().strip('Google Chrome ').strip('Chromium ').strip() if install_path else version
    
    return int(full_version.split('.')[0]) if full_version else fallback_version
