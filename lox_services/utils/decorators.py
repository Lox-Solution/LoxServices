"""All general custom python decorators"""
# pylint: disable=invalid-name
from datetime import datetime
from functools import reduce
from pprint import pprint
from time import perf_counter
import time
from typing import Callable, Tuple, Type

from pyvirtualdisplay import Display

from lox_services.config.env_variables import get_env_variable
from lox_services.utils.enums import Colors
from lox_services.utils.general_python import (
    colorize,
    convert_bytes_to_human_readable_size_unit,
    print_info,
)


def production_environment_only(function: Callable):
    """Decorator to ensure that a function is only ran in production environment.

    Args:
        func (function): Function to be decorated.
    """

    def wrapper(*args, **kwargs):
        if get_env_variable("ENVIRONMENT") != "production":
            print("This function should only be ran in production environment.")
            raise RuntimeError(
                "This function should only be ran in production environment."
            )
        else:
            return function(*args, **kwargs)

    return wrapper


def Perf(function: Callable):
    """Prints the performance of the decorated function."""

    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        print(
            colorize(
                f"Start of function '{function.__name__}' : {datetime.now()}",
                Colors.YELLOW,
            )
        )
        ret = function(*args, **kwargs)
        end_time = perf_counter()
        print(
            colorize(
                f"Function '{function.__name__}' took {round(end_time-start_time,2)}secs to execute.",
                Colors.YELLOW,
            )
        )
        return ret

    return wrapper


def LogArguments(function: Callable):
    """Pretty prints the aruments of the decorated function."""

    def wrapper(*args, **kwargs):
        print("args:")
        pprint(args)
        print("kwargs:")
        pprint(kwargs)
        function(*args, **kwargs)

    return wrapper


def DataUsage(function: Callable):
    """To be used only when the result of the function is an array of requests.Response."""

    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        try:
            bytes_size = reduce(
                lambda acc, val: acc + val,
                map(lambda response: len(response.content), result),
            )
        except TypeError:
            bytes_size = 0
        value, unit = convert_bytes_to_human_readable_size_unit(bytes_size)
        print_info(f"{value} {unit} of data fetched.")
        return result

    return wrapper


def VirtualDisplay(function: Callable):
    """Uses a virtual display to run the decorated function when ENVIRONMENT is set to production."""

    def wrapper(*args, **kwargs):
        is_production = get_env_variable("ENVIRONMENT") == "production"
        if is_production:
            display = Display(visible=0, size=(1920, 1200), backend="xvfb")
            display.start()

        result = function(*args, **kwargs)

        if is_production:
            display.stop()

        return result

    return wrapper


def retry(
    max_attempts: int,
    exceptions_handled: Tuple[Type[BaseException], ...] = Exception,
    delay: int = 5,
):
    """
    Decorator function that retries the decorated function for a maximum number of attempts.

    Args:
        max_attempts (int): Maximum number of attempts to retry the decorated function.
        exceptions_handled (Tuple[Type[BaseException], ...], optional): Tuple of exception types to be handled. Defaults to Exception.
        delay (int, optional): Delay in seconds between retries. Defaults to 5.

    Returns:
        function: Decorator function that retries the decorated function.

    Raises:
        BaseException: If the decorated function fails after the maximum number of attempts.

    Usage:
        @retry(max_attempts=3, exceptions_handled=(CustomException,), delay=2)
        def my_function():
            # Code to retry

    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions_handled as e:
                    attempts += 1
                    print(
                        f"Attempt {attempts} failed fro function {func.__name__}: {e}"
                    )
                    time.sleep(delay)

                    if attempts == max_attempts:
                        print(f"Function failed after {max_attempts} attempts")
                        raise e

        return wrapper

    return decorator
