import inspect
from typing import List


def get_function_callers() -> List[str]:
    """Gets the function names that called a function + its own name at first index 0.
    Deepeness of function calls is propagated through the indexes.

    ## Example
        >>> def f1(): get_function_callers()
        >>> def f2(): f1()
        >>> def f3(): f2()

        >>> f1() # ['f1', 'f2', 'f3']
    """
    current_frame = inspect.currentframe()
    if not current_frame:
        return None

    current_function_name = current_frame.f_code.co_name
    caller_frame = inspect.getouterframes(current_frame)
    caller_names = list(
        filter(
            lambda caller: caller not in [current_function_name, "<module>"],
            map(lambda frame: frame[3], caller_frame),
        )
    )
    return caller_names
