import os
import re
import sys

from lox_services.utils.general_python import print_info


def extract_version_registry(output: str) -> str:
    """Extracts the version of Chrome from the registry output for Windows machines.

    Args:
        output (str): The output of the registry query.
    """
    google_version = ""
    for letter in output[output.rindex("DisplayVersion    REG_SZ") + 24 :]:
        if letter != "\n":
            google_version += letter
        else:
            break
    return google_version.strip()


def extract_version_folder() -> str:
    """Check if the Chrome folder exists in the x32 or x64 Program Files folders for Windows machines.

    Returns:
        str: The version of Chrome.
    """
    for i in range(2):
        path = (
            "C:\\Program Files"
            + (" (x86)" if i else "")
            + "\\Google\\Chrome\\Application"
        )
        if os.path.isdir(path):
            paths = [f.path for f in os.scandir(path) if f.is_dir()]
            for path in paths:
                filename = os.path.basename(path)
                pattern = r"\d+\.\d+\.\d+\.\d+"
                match = re.search(pattern, filename)
                if match and match.group():
                    # Found a Chrome version.
                    return match.group(0)
    raise RuntimeError("Chrome version not found.")


def get_platform() -> str:
    """Get the platform of the machine.

    Raises:
        RuntimeError: If the platform is not supported.

    Returns:
        str: The platform of the machine.
    """
    if sys.platform in ["linux", "linux2"]:
        return "linux"
    elif sys.platform == "darwin":
        return "mac"
    elif sys.platform in ["win32", "cygwin", "msys"]:
        return "windows"
    else:
        raise RuntimeError("Platform not supported.")


def get_chrome_version(fallback_version: int = 139) -> int:
    """Get the version of Chrome installed on the machine.

    Args:
        fallback_version (int): The version to return, if the chrome version is not found by script. Defaults to 109.

    Returns:
        int: The version of Chrome. If version is not found, return fallback_version.
    """
    version = None
    install_path = None
    platform_name = get_platform()

    try:
        if platform_name == "linux":
            # Check the path of chrome and chromium in linux and return path for version
            install_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromedriver",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/opt/google/chrome/google-chrome",
            ]
            for path in install_paths:
                if os.path.exists(path):
                    install_path = path
                    print(f"Found Chrome at {path}")
                    break

        elif platform_name == "mac":
            # OS X
            install_path = (
                r"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
            )
        elif platform_name == "windows":
            install_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            for path in install_paths:
                if os.path.exists(path):
                    install_path = path
                    break

            if install_path:
                try:
                    version = extract_version_folder()
                except Exception as e:
                    print_info(f"Failed to extract version from folder: {e}")

    except Exception as ex:
        print_info(
            f"Error while getting Chrome version: {ex}, returning deault version {fallback_version}."
        )

    full_version = (
        os.popen(f"{install_path} --version")
        .read()
        .strip("Google Chrome ")
        .strip("Chromium ")
        .strip()
        if install_path
        else version
    )

    return int(full_version.split(".")[0]) if full_version else fallback_version


# if __name__ == "__main__":
#     print(get_chrome_version())
