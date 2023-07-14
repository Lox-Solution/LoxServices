import unittest
import os
from datetime import datetime
from typing import List, Optional, Tuple
import pandas as pd
from lox_services.utils.general_python import (
    colorize,
    print_info,
    print_error,
    print_success,
    print_step,
    is_file_or_folder_path,
    safe_mkdir,
    safe_open,
    safe_listdir,
    safe_to_csv,
    string_search,
    is_one_element_substring,
    string_search_from_series,
    convert_bytes_to_human_readable_size_unit,
    get_file_size,
    safe_remove,
    get_folder_size,
    convert_date_with_foreign_month_name,
    format_snake_case_to_human_upper_case,
    format_amount_to_human_string,
    convert_sym_to_code,
    split_array,
    split_date_range,
    rreplace,
    remove_all_file_with_format_from_folder,
    remove_extra_comma_dot_from_float,
)


class TestUtilsFunctions(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.join(
            os.path.dirname(__file__),
            "Files",
        )
        self.test_folder = os.path.join(self.base_dir, "general_python")

        self.test_file = os.path.join(self.base_dir, "dummy.csv")

        os.path.join(self.base_dir, "test_image.png")
        if not os.path.exists(self.test_folder):
            os.mkdir(self.test_folder)

    def test_print_info(self):
        # Redirect print output to check if it contains the expected colorized string
        import sys
        from io import StringIO

        sys.stdout = StringIO()
        print_info("Test")
        output = sys.stdout.getvalue()
        self.assertIn("\x1b[33mTest\x1b[0m", output)

        # Reset print output
        sys.stdout = sys.__stdout__

    def test_print_error(self):
        # Redirect print output to check if it contains the expected colorized string
        import sys
        from io import StringIO

        sys.stdout = StringIO()
        print_error("Test")
        output = sys.stdout.getvalue()
        self.assertIn("\x1b[31mTest\x1b[0m", output)

        # Reset print output
        sys.stdout = sys.__stdout__

    def test_print_success(self):
        # Redirect print output to check if it contains the expected colorized string
        import sys
        from io import StringIO

        sys.stdout = StringIO()
        print_success("Test")
        output = sys.stdout.getvalue()
        self.assertIn("\x1b[32mTest\x1b[0m", output)

        # Reset print output
        sys.stdout = sys.__stdout__

    def test_print_step(self):
        # Redirect print output to check if it contains the expected colorized string
        import sys
        from io import StringIO

        sys.stdout = StringIO()
        print_step(1)
        output = sys.stdout.getvalue()
        expected_output = "\x1b[34m\n     _\n    | |    _____  __\n    | |   / _ \\ \\/ /\n    | |__| (_) >  <      STEP 1\n    |_____\\___/_/\\_\\\n\x1b[0m\n"
        self.assertEqual(output, expected_output)

        # Reset print output
        sys.stdout = sys.__stdout__

    def test_is_file_or_folder_path(self):
        self.assertEqual(is_file_or_folder_path(self.test_file), "file")
        self.assertEqual(is_file_or_folder_path(self.test_folder), "folder")
        self.assertRaises(ValueError, is_file_or_folder_path, "path/to/file//.txt")
        self.assertRaises(ValueError, is_file_or_folder_path, "path/to/invalid/file")
        self.assertRaises(ValueError, is_file_or_folder_path, "path/to/invalid/folder/")

    def test_safe_mkdir(self):
        # Case 1: Folder does exist
        test_dir = os.path.join(self.test_folder, "test_dir")
        safe_mkdir(test_dir)
        self.assertTrue(os.path.exists(test_dir))
        os.rmdir(test_dir)

        # Case 2: Folder does not exist
        with self.assertRaises(ValueError):
            safe_mkdir("//wrong_path//")

    def test_safe_open(self):
        test_file = os.path.join(self.test_folder, "test.txt")
        with safe_open(test_file, "w") as f:
            f.write("Test")
        self.assertTrue(os.path.exists(test_file))
        os.remove(test_file)

    def test_safe_listdir(self):
        test_dir = os.path.join(self.test_folder, "test_dir")
        os.makedirs(test_dir)
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test")
        files = list(safe_listdir(test_dir))
        self.assertEqual(files, ["test.txt"])
        os.remove(test_file)
        os.rmdir(test_dir)

    def test_safe_to_csv(self):
        test_file = os.path.join(self.test_folder, "test.csv")
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        safe_to_csv(df, test_file)
        self.assertTrue(os.path.exists(test_file))
        os.remove(test_file)

    def test_string_search(self):
        self.assertTrue(
            string_search("alpha", ["I am alpha", "You are beta"], mode="left")
        )
        self.assertTrue(string_search("I am alpha", ["alpha", "beta"], mode="right"))
        self.assertTrue(
            string_search(
                "I am gamma", ["I am gamma and I love epsilon", "gamma"], mode="union"
            )
        )
        self.assertFalse(string_search("I am alpha", ["beta", "gamma"], mode="right"))
        self.assertFalse(string_search("I am gamma", ["alpha", "beta"], mode="union"))

        # Case: Invalid mode
        with self.assertRaises(Exception):
            string_search("alpha", ["I am alpha", "You are beta"], mode="invalid")

    def test_is_one_element_substring(self):
        self.assertTrue(
            is_one_element_substring("app", ["apple", "banana", "orange"])[0]
        )
        self.assertTrue(
            is_one_element_substring(
                "apple", ["apple", "banana", "orange"], full_string=True
            )[0]
        )
        self.assertFalse(is_one_element_substring("apple", ["orange", "banana"])[0])

    def test_string_search_from_series(self):
        series = pd.Series(["I am alpha", "You are beta"])
        strings = ["alpha", "beta"]
        result = string_search_from_series(series, strings)
        self.assertEqual(result, [True, True])

    def test_get_file_size(self):
        test_file = os.path.join(self.test_folder, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test")
        size = get_file_size(test_file)
        self.assertEqual(size, (4.0, "BYTES"))
        os.remove(test_file)

    def test_safe_remove(self):
        test_file = os.path.join(self.test_folder, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test")
        safe_remove(test_file)
        self.assertFalse(os.path.exists(test_file))

        # Case 2: File does not exist, no Exception should be raise
        raised = False
        try:
            safe_remove("/path/to/nonexistent/file.txt")
        except:
            raised = True

        self.assertFalse(raised)

    def test_get_folder_size(self):
        test_dir = os.path.join(self.test_folder, "test_dir")
        os.makedirs(test_dir)
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test")

        # Case 1: Folder does exist
        size = get_folder_size(test_dir)
        self.assertEqual(size, (4.0, "BYTES"))

        # Case 3: tmp in exlcluded from the size
        tmp_file = os.path.join(test_dir, "tmp")
        with open(tmp_file, "w") as f:
            f.write("Test")
        size = get_folder_size(test_dir)
        self.assertEqual(size, (4.0, "BYTES"))
        os.remove(tmp_file)

        # Case 4: Folder inside the folder and return human non readable
        test_dir_2 = os.path.join(test_dir, "test_dir_2")
        os.makedirs(test_dir_2)
        test_file_dir_2 = os.path.join(test_dir_2, "test.txt")
        with open(test_file_dir_2, "w") as f:
            f.write("Test")

        size = get_folder_size(test_dir, False)
        self.assertEqual(size, 8.0)

        size = get_folder_size(test_dir_2, False)
        self.assertEqual(size, 4.0)
        os.remove(test_file_dir_2)
        os.rmdir(test_dir_2)

        os.remove(test_file)
        os.rmdir(test_dir)

    def test_convert_date_with_foreign_month_name(self):
        # Case 1: Month name is in the list
        date = convert_date_with_foreign_month_name("2021", "jan", "15")
        self.assertEqual(date, datetime(2021, 1, 15))

        # Case 2: Month name is not in the list
        with self.assertRaises(Exception):
            convert_date_with_foreign_month_name("2021", "invalid", "15")

    def test_format_snake_case_to_human_upper_case(self):
        formatted_string = format_snake_case_to_human_upper_case("hello_world")
        self.assertEqual(formatted_string, "Hello World")

    def test_format_amount_to_human_string(self):
        # Case 1: Amount is a string
        formatted_amount = format_amount_to_human_string("120050.10", "€")
        self.assertEqual(formatted_amount, "€120,050.10 ")

        # Case 2: Language is FR
        formatted_amount = format_amount_to_human_string("120050.10", "FR", "€")
        self.assertEqual(formatted_amount, "120,050.10 €")

        # Case 3: Value is null
        formatted_amount = format_amount_to_human_string(None, "€")
        self.assertEqual(formatted_amount, "")

        # Case 4: Value is null
        formatted_amount = format_amount_to_human_string("wrong_amount", None, None)
        self.assertEqual(formatted_amount, "wrong_amount")

        # Case 5: Exception on the cents
        formatted_amount = format_amount_to_human_string("1000")
        self.assertEqual(formatted_amount, "€1,000.00 ")

        # Case 5: Handle less than 2 cents digits
        formatted_amount = format_amount_to_human_string("1000.0")
        self.assertEqual(formatted_amount, "€1,000.00 ")

    def test_convert_sym_to_code(self):
        # Case 1: Currency symbol is in the list
        currency_code = convert_sym_to_code("$")
        self.assertEqual(currency_code, "USD")

        # Case 2: Currency symbol is not in the list
        with self.assertRaises(KeyError):
            currency_code = convert_sym_to_code("-")

    def test_split_array(self):
        original_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        split_arrays = split_array(original_array, 4)
        expected_result = [[1, 2, 3], [4, 5, 6], [7, 8], [9, 10]]
        self.assertEqual(split_arrays, expected_result)

    def test_split_date_range(self):
        start = "2015-01-01"
        end = "2015-02-28"
        date_range = list(split_date_range(start, end, 4))
        expected_result = [
            "2015-01-01",
            "2015-01-15",
            "2015-01-30",
            "2015-02-13",
            "2015-02-28",
        ]
        self.assertEqual(date_range, expected_result)

    def test_rreplace(self):
        replaced_string = rreplace("a.b.c.d.e", ".", "-", 2)
        self.assertEqual(replaced_string, "a.b.c-d-e")

    def test_remove_all_file_with_format_from_folder(self):
        test_dir = os.path.join(self.test_folder, "test_dir")
        os.makedirs(test_dir)
        test_file1 = os.path.join(test_dir, "test1.txt")
        test_file2 = os.path.join(test_dir, "test2.csv")
        test_file3 = os.path.join(test_dir, "test3.csv")
        with open(test_file1, "w") as f:
            f.write("Test 1")
        with open(test_file2, "w") as f:
            f.write("Test 2")
        with open(test_file3, "w") as f:
            f.write("Test 3")

        # Case 1: Good format
        ignored_files = ["test3.csv"]
        deleted_files = remove_all_file_with_format_from_folder(
            file_format="csv",
            folder_path=test_dir,
            ignored_files=ignored_files,
            recursive=False,
        )
        self.assertEqual(deleted_files, [test_file2])
        self.assertTrue(os.path.exists(test_file1))
        self.assertTrue(os.path.exists(test_file3))

        # Case 2: Wrong file format
        with self.assertRaises(ValueError):
            deleted_files = remove_all_file_with_format_from_folder(
                file_format="txt",
                folder_path=test_dir,
                ignored_files=ignored_files,
                recursive=False,
            )

        os.remove(test_file1)
        os.remove(test_file3)

        # Case 3: Wrong folder path
        deleted_files = remove_all_file_with_format_from_folder(
            file_format="csv",
            folder_path="wrong_path",
            ignored_files=ignored_files,
            recursive=False,
        )
        self.assertEqual(deleted_files, [])

        # Case 4: Recursive
        test_dir_2 = os.path.join(test_dir, "test_dir_2")
        os.makedirs(test_dir_2)
        file_dir_2 = os.path.join(test_dir, "test_dir_2_file.csv")
        with open(file_dir_2, "w") as f:
            f.write("Test dir 2")

        deleted_files = remove_all_file_with_format_from_folder(
            file_format="csv",
            folder_path=test_dir,
            ignored_files=ignored_files,
            recursive=True,
        )
        self.assertEqual(deleted_files, [file_dir_2])

        os.rmdir(test_dir_2)
        os.rmdir(test_dir)

    def test_remove_extra_comma_dot_from_float(self):
        # Case 1: Thousand separator is dot
        number = remove_extra_comma_dot_from_float("1.789.423,45")
        self.assertEqual(number, 1789423.45)

        # Case 2: Thousand separator is comma
        number = remove_extra_comma_dot_from_float("1,789,423.45")
        self.assertEqual(number, 1789423.45)

        # Case 3: Only dot separators
        number = remove_extra_comma_dot_from_float("1.789.423.00")
        self.assertEqual(number, 1789423.0)

        # Case 4: Only comma separators
        number = remove_extra_comma_dot_from_float("1,789,423,00")
        self.assertEqual(number, 1789423.0)


if __name__ == "__main__":
    unittest.main()
