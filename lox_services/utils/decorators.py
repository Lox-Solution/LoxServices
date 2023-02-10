"""All general custom python decorators"""
# pylint: disable=invalid-name
from datetime import datetime
from functools import reduce
from pprint import pprint
from time import perf_counter
from typing import Callable

from pyvirtualdisplay import Display

from lox_services.config.env_variables import get_env_variable
from lox_services.utils.enums import Colors
from lox_services.utils.general_python import colorize, convert_bytes_to_human_readable_size_unit, print_info


def Perf(function: Callable):
    """Prints the performance of the decorated function."""
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        print(colorize(f"Start of function '{function.__name__}' : {datetime.now()}",Colors.YELLOW))
        ret = function(*args, **kwargs)
        end_time = perf_counter()
        print(colorize(f"Function '{function.__name__}' took {round(end_time-start_time,2)}secs to execute.",Colors.YELLOW))
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
            bytes_size = reduce(lambda acc, val: acc + val, map(lambda response: len(response.content), result))
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
            display = Display(
                visible=0,
                size=(1920, 1200),
                backend="xvfb"
            )
            display.start()
            
        result = function(*args, **kwargs)
        
        if is_production:
            display.stop()
        
        return result
    
    return wrapper
