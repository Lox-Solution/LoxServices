import os
import re
from sys import platform

def extract_version_registry(output):
    """Extracts the version of Chrome from the registry output.

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

def extract_version_folder():
    """Check if the Chrome folder exists in the x32 or x64 Program Files folders.

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

def get_chrome_version():
    """Get the version of Chrome installed on the machine.

    Returns:
        int: The version of Chrome. If version is not found, returns 109.
    """
    version = None
    install_path = None

    try:
        if platform == "linux" or platform == "linux2":
            # linux
            install_path = "/usr/bin/google-chrome"
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
        print(ex)

    full_version = os.popen(f"{install_path} --version").read().strip('Google Chrome ').strip() if install_path else version
    
    return int(full_version.split('.')[0]) if full_version else 109
