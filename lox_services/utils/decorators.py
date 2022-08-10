"""All general custom python decorators"""
# pylint: disable=invalid-name
from datetime import datetime
from functools import reduce
from pprint import pprint
from time import perf_counter
from typing import Callable

from lox_services.utils.enums import Colors
from lox_services.utils.general_python import colorize, convert_bytes_to_human_readable_size_unit, print_info


def Perf(function: Callable):
    """Prints the performance of the decorated function."""
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        print(colorize(f"Start of function '{function.__name__}' : {datetime.now()}",Colors.Yellow))
        ret = function(*args, **kwargs)
        end_time = perf_counter()
        print(colorize(f"Function '{function.__name__}' took {round(end_time-start_time,2)}secs to execute.",Colors.Yellow))
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
    def DataUsageDecoratorWrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        try:
            bytes_size = reduce(lambda acc, val: acc + val, map(lambda response: len(response.content), result))
        except TypeError:
            bytes_size = 0
        value, unit = convert_bytes_to_human_readable_size_unit(bytes_size)
        print_info(f"{value} {unit} of data fetched.")
        return result
    
    return DataUsageDecoratorWrapper
