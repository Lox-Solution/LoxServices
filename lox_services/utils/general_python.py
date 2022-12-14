"""
Defines some utils functions for the project.
"""
import os
import re
import time
import unicodedata
from datetime import datetime
from typing import Iterator, List, Literal, Tuple

import pandas as pd

from lox_services.utils.enums import SIZE_UNIT, Colors


def colorize(string: str, color: Colors):
    """Format a string to print it with a certain color in the terminal."""
    return f"\x1b[{color.value}m{string}\x1b[0m"


def print_info(string: str):
    """Format a string to error style."""
    print(colorize(string, Colors.Yellow))


def print_error(string: str):
    """Format a string to error style."""
    print(colorize(string, Colors.Red))


def print_success(string: str):
    """Format a string to a success style."""
    print(colorize(string, Colors.Green))


def print_step(step):
    """Format the log message for the begining of a step."""
    # pylint: disable=anomalous-backslash-in-string
    print(colorize(
f"""
     _
    | |    _____  __
    | |   / _ \ \/ /
    | |__| (_) >  <      STEP {step}
    |_____\___/_/\_\\
""",Colors.Blue))


FileOrFolder = Literal["file","folder"]
def is_file_or_folder_path(path: str) -> FileOrFolder:
    """Checks if a path leads to a file or a folder.
        ## Arguments
        - `path`: The path to be checked
        
        ## Returns
        - "file" if the given path is a file
        - "folder" if the given path is a folder
    """
    
    path = ''.join((c for c in unicodedata.normalize('NFD', path) if unicodedata.category(c) != 'Mn'))
    if re.match(r'.*(//)+.*',path):
        raise ValueError('The given path is not a valid file or folder.')
    if re.match(r'(?:/[^/]+)+?/[\w_ -:]+\.\w+$',path):
        return "file"
    elif re.match(r'(?:/[^/]+)+?/[\w_ -:]+',path):
        return "folder"
    else:
        raise ValueError('The given path is not a valid file or folder.')


# Taken from https://stackoverflow.com/a/600612/119527
def safe_mkdir(path: str) -> None:
    """Creates all parents directories of a file if they don't exist, or all directories of a directory path."""
    path_type = is_file_or_folder_path(path)
    try:
        if path_type == 'file':
            os.makedirs(os.path.dirname(path))
        elif path_type == "folder":
            os.makedirs(path)
        else:
            raise ValueError("The given path is neither a file nor a folder.")
    except FileExistsError:
        pass


def safe_open(path: str, mode: str):
    """Open "path", creating any parent directories as needed."""
    safe_mkdir(path)
    return open(path, mode)


def safe_listdir(path: str) -> list:
    """List directories of a "path", creating any parent directories as needed, and removing __pycache__ files."""
    safe_mkdir(path)
    return filter(lambda file_name: file_name != '__pycache__',os.listdir(path))


def safe_to_csv(df, path) -> None:
    """Creates a csv from a dataframe, creating any parent directories as needed."""
    safe_mkdir(path)
    df.to_csv(path)


StringSearchMode = Literal["left","right","union"]
def string_search(string: str, list_of_strings: List[str], *, mode: StringSearchMode = "left", case_sensitive=False)-> bool:
    """Searches if a string is in a list of strings. 
        Or if any element in a list of strings is in a string.
        Or both.
        
        ## Arguments
        - `string`: The single string affected by the search.
        - `list_of_strings`: The list of strings affected by the search.
        - `mode`: 
            - "left": Looks for at least one occurence of the string parameter in the list parameter.
            - "right": Looks for at least one occurence of every string in the list into the string parameter.
            - "union": Checks if one of the two previous mode is valid.
        - `case_sensitive`: Checks the case if set to True
        
        ## Example
            >>> string_search("alpha", ["I am alpha", "You are beta"], mode= "left")
            # True, "alpha" is in "I am alpha"
            >>> string_search("I am alpha", ["alpha", "beta"], mode= "right")
            # True, "alpha" is in "I am alpha"
            >>> string_search("I am gamma", ["I am gamma and I love epsilon", "gamma"], mode= "union")
            # True, "gamma" is in "I am gamma" or "I am gamma" is in "I am gamma and I love epsilon" 
        
        ## Returns
        - True if the match is correct
        - False otherwise    
    """
    if not case_sensitive : 
        string = string.lower()
        list_of_strings = list(map(str.lower, list_of_strings))
    left: bool = any(str(string) in str(str_element) for str_element in list_of_strings)
    right: bool = any(str(str_element) in str(string) for str_element in list_of_strings)
    if mode == "left": 
        return left
    elif mode == "right": 
        return right
    elif mode == "union": 
        return left or right
    else: 
        raise Exception("Wrong mode. Please refer to function documentation.")


def string_search_from_series(serie: pd.Series, strings: List[str]) -> List[bool]:
    """Does a string search from a pandas Series and returns a list of booleans.
        This is mainly used for filtering dataframes.
    """
    return [string_search(value, strings, mode="right") for value in serie.values]


def convert_bytes_to_human_readable_size_unit(size: int) -> Tuple[float, str]:
    formated_size = 0
    size_unit = SIZE_UNIT.BYTES
    for unit in SIZE_UNIT:
        byte_value = 1024**(unit.value-1)
        if size > byte_value:
            formated_size = size/(byte_value)
            size_unit = unit
    return round(formated_size,2), size_unit.name


def get_file_size(file_path: str) -> Tuple[float,str]:
    """Gets file in size in given unit like KB, MB or GB"""
    size = os.path.getsize(file_path)
    return convert_bytes_to_human_readable_size_unit(size)


def safe_remove(file_path: str):
    "Remove a file if existing"
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print("File does not exist")
        pass


def get_folder_size(folder_path: str, _human_readable = True):
    """Gets a folder size in given unit like KB, MB or GB."""
    total_size = 0
    for file_or_folder_name in os.listdir(folder_path):
        if file_or_folder_name in ['tmp']:
            continue
        
        file_or_folder_path = os.path.join(folder_path, file_or_folder_name)
        if os.path.isfile(file_or_folder_path):
            total_size += os.path.getsize(file_or_folder_path)
        else:
            total_size += get_folder_size(file_or_folder_path, False)
    
    if _human_readable:
        return convert_bytes_to_human_readable_size_unit(total_size)
    
    return total_size


def convert_date_with_foreign_month_name(year: str, month: str, day: str) -> datetime:
    """Converts a date with a foreign month name to a datetime.
        ## Returns 
        A datetime instance
    """
    month_d = {
        '01': ['jan', 'january'],
        '02': ['feb', 'fev', 'february'],
        '03': ['mar', 'mrt', 'march'],
        '04': ['apr', 'avr', 'april'],
        '05': ['may', 'mei', 'mai', 'may'],
        '06': ['jun', 'june'],
        '07': ['jul', 'july'], 
        '08': ['aug', 'aou', 'august'],
        '09': ['sep', 'sept', 'september'],
        '10': ['oct', 'okt', 'october'],
        '11': ['nov', 'november'],
        '12': ['dec', 'december']
    }
    
    month = month.replace('.', '')
    if month.isalpha(): # change from letters to numbers
        try:
            month = [k for k, v in month_d.items() if month.lower() in v][0]
        except Exception as e:
            raise Exception('The following month is not mapped', month.lower()) from e
    
    return datetime(int(year), int(month), int(day))


def format_snake_case_to_human_upper_case(string: str) -> str:
    """Format snake case into upper case words.
        ## Example
            >>> format_snake_case_to_human_upper_case("hello_world")
                # Hello World
    """
    return ' '.join(map(lambda x: x.capitalize(), string.split('_')))


def format_amount_to_human_string(value, language="EN", currency="€") -> str:
    """Formats a float or an int into a human-readable string with it's currency
        ## Arguments
        - `value`: The value to format.
        - `currency`: The currency to add at the end of the string.
        - `language`: The language used, needed to place the currency symbol.
        
        ## Example
            >>> format_amount_to_human_string("120050.10","$")
                # $120,050.10
        
        ## Returns
        - The formatted amount with currency.
        - The original string if the value was not a number.
    """
    number_of_numbers_by_group = 3
    try:
        if value is None or value == 'None' or value != value: #Check nan, None, and "None"
            return ''
        float(value)
        string = str(value)
        splited_cents = string.split('.')
        try:
            cents = splited_cents[1]
            if len(cents) < 2:
                for _ in range(2-len(cents)):
                    cents += "0"
        except IndexError:
            cents = "00"
        splited = []
        #We do it reversed to start from the unit, otherwise we can have results like 123,00.00
        for high_index in range(len(splited_cents[0]),0,-number_of_numbers_by_group):
            low_index = high_index - number_of_numbers_by_group if high_index - number_of_numbers_by_group >= 0 else 0
            splited.append(splited_cents[0][low_index: high_index])
        if language == 'FR':
            prefix = ''
            suffix = currency
        else:
            prefix = currency
            suffix = ''
        return f"{prefix}{','.join(splited[::-1])}.{cents} {suffix}"
    except Exception:
        return value


def split_array(array: List[List], number_of_sub_arrays: int):
    """Creates a list of `n` sub-arrays coming from the original array.
        ## Arguments
        -`array`: The original array to split into sub-arrays.
        -`number_of_sub_arrays`: Number of elements to create.
        
        ## Example
            >>> original_array = [1,2,3,4,5,6,7,8,9,10]
            >>> split_array(original_array, 4)
            # [[1, 2, 3], [4, 5, 6], [7, 8], [9, 10]]
    """
    k, m = divmod(len(array), number_of_sub_arrays)
    return list(array[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(number_of_sub_arrays))


def split_date_range(start: datetime, end: datetime, intv: int, output_format: str = "%Y-%m-%d") -> Iterator[datetime]:
    """Creates an Iterator of `n` intervals between two dates.
        ## Arguments
        -`start`: The start date used for the split, in the format %Y-%m-%d.
        -`end`: The end date used for the split, in the format %Y-%m-%d.
        -`intv`: The number of times the interval need to be split into.
        -`output_format`: The format for each date returned
        
        ## Returns
        - The list containing all dates in the format %Y-%m-%d
        
        ## Example
            >>> begin = '20150101'
            >>> end = '20150228'
            >>> list(date_range(begin, end, 4))
            # ['20150101', '20150115', '20150130', '20150213', '20150228']
    """
    
    start = datetime.strptime(start,"%Y-%m-%d")
    end = datetime.strptime(end,"%Y-%m-%d")
    
    diff = (end  - start ) / intv
    
    for i in range(intv):
        yield (start + diff * i).strftime(output_format)
    yield end.strftime(output_format)


def rreplace(s: str, old: str, new: str, occurrence: int)->str:
    """Replace the n last occurence of an expression in a string and return it
    ## Arguments
        -`s`: The string you want to modify
        -`old`: the expression to replace
        -`new`: the expression to replace with
        -`occurence`: the number of occurence to replace
    """
    return new.join(s.rsplit(old, occurrence))


def remove_all_file_with_format_from_folder(
    *, 
    file_format:  str, 
    folder_path: str, 
    ignored_files : List[str] = [], 
    recursive: bool = False) -> List[str]:
    """Remove all file of a given format that are in a folder.
    ## Arguments
    - 'file_format' : kind of file you want to remove, either "csv", "xlsx", "pdf" (to avoid deleting everything in one run)
    - 'folder_path' : Path of the folder to clean.
    - 'ignored_files' : list of file NAME to not delete. default value : []
    - 'recursive' : make the function recursive on subfolder if true. default value : False
    
    ## Returns
    List of deleted files;
    
    ## Example
    >>> remove_all_file_with_type_from_folder(
        file_format = "csv", 
        folder_path = "/home/output_folder", 
        ignored_file = ["to_keep.csv","hello_world.csv"])
    """
    if file_format not in ["csv", "xlsx", "pdf"]:
        raise ValueError(f"file_format has to be in ['csv', 'xlsx', 'pdf'] and it's '{file_format}'")
    extension = "."+file_format
    
    deleted_files = []
    if not os.path.exists(folder_path):
        print("Folder path does not exists.")
        return deleted_files
    
    
    for obj in os.listdir(folder_path):
        obj_path = os.path.join(folder_path, obj)
        
        if os.path.isdir(obj_path):
            if recursive:
                deleted_files = deleted_files + remove_all_file_with_format_from_folder(
                    file_format = file_format, 
                    folder_path= obj_path,
                    ignored_files= ignored_files, 
                    recursive= True)
        
        elif obj.endswith(extension) and obj not in ignored_files:
            os.remove(obj_path)
            deleted_files.append(obj_path)
            
    return deleted_files
        


def remove_extra_comma_dot_from_float(float_string: str) -> float:
    """remove any useless comma or thousands separators from a float and return the associated float value
    ##Examples
    >>> remove_extra_comma_dot_from_float("1.789.423,45") #returns 1789423.45
    >>> remove_extra_comma_dot_from_float("1,789,423.45") #returns 1789423.45
    """
    try:
        return float(float_string)
    except ValueError:
        pass
    float_string = str(float_string)
    
    try :
        last_dot = float_string.rindex(".") 
    except ValueError:
        last_dot = -1
    
    try :
        last_comma = float_string.rindex(",") 
    except ValueError:
        last_comma = -1
        
    if last_comma > last_dot:
        float_formated_number = float_string[:last_comma].replace(",","").replace(".","")+float_string[last_comma:].replace(",",".")
    else:
        float_formated_number = float_string[:last_dot].replace(",","").replace(".","")+float_string[last_dot:]
    
    return float(float_formated_number)
