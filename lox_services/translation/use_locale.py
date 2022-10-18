import datetime
import locale
import os
import subprocess


def get_all_locales():
    """Returns a list of all installable locales.
    """
    return locale.locale_alias


def download_locale(language_code: str, encoding: str):
    """Downloads the locale for the given language.
        ## Example
        >>> download_locale('fr_FR', 'utf8')
    """
    if language_code.lower() not in get_all_locales():
        raise Exception(f"Locale '{language_code}' is not installable.")
    
    download_locale_filepath = os.path.join(os.path.dirname(__file__), 'download_locale.sh')
    subprocess.check_call([download_locale_filepath, language_code, encoding])


def use_locale(language_code: str, encoding: str = 'utf8'):
    """Sets the locale for the current thread to the given language and encoding.
        ## Example
        >>> use_locale('fr_FR')
    """
    download_locale(language_code, encoding)
    
    try:
        locale.setlocale(locale.LC_TIME, f"{language_code}.{encoding}")
    
    except locale.Error as local_error:
        raise Exception(f"Locale '{language_code}' is installed but the current process is not aware of it. Please relauch command.") from local_error


if __name__ == '__main__':
    use_locale('ru_RU')
    month = datetime.datetime.today().strftime("%B").capitalize()
    print(month)
