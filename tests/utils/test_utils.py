import os
import unittest
import datetime

from lox_services.utils.decorators import Perf

from lox_services.utils.general_python import (
    convert_bytes_to_human_readable_size_unit,
    convert_date_with_foreign_month_name,
    format_amount_to_human_string,
    format_snake_case_to_human_upper_case,
    is_file_or_folder_path,
    get_file_size,
    get_folder_size,
    rreplace,
    split_array,
    split_date_range,
    is_one_element_substring,
)


PDF_ASSETS_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "lox_services", "pdf", "assets"
)
file_path = os.path.join(PDF_ASSETS_PATH, "pdf_tables.css")


class TestFilesAndFoldersFunctions(unittest.TestCase):
    def test_is_file_or_folder_path(self):
        self.assertEqual(is_file_or_folder_path(file_path), "file")
        self.assertNotEqual(is_file_or_folder_path(file_path), "folder")
        self.assertEqual(is_file_or_folder_path(PDF_ASSETS_PATH), "folder")
        self.assertNotEqual(is_file_or_folder_path(PDF_ASSETS_PATH), "file")
        self.assertRaises(
            ValueError,
            is_file_or_folder_path,
            os.path.join(PDF_ASSETS_PATH, "//EN.json"),
        )

    def test_get_file_or_folder_size(self):
        self.assertGreater(get_file_size(file_path), (0, "BYTES"))
        self.assertGreater(get_folder_size(PDF_ASSETS_PATH), (0, "BYTES"))


class TestConvertAndFormatFunctions(unittest.TestCase):
    def test_convert_functions(self):
        self.assertEqual(
            convert_bytes_to_human_readable_size_unit(12345), (12.06, "KB")
        )
        self.assertEqual(
            convert_date_with_foreign_month_name("2022", "feb", "21"),
            datetime.datetime(2022, 2, 21, 0, 0),
        )

    def test_format_functions(self):
        self.assertEqual(
            format_snake_case_to_human_upper_case("hello_world"), "Hello World"
        )
        self.assertEqual(
            format_amount_to_human_string("120050.10", "EN", "€"), "€120,050.10 "
        )
        self.assertEqual(
            format_amount_to_human_string("120050.10", "FR", "$"), "120,050.10 $"
        )


class TestSplitAndReplaceFunctions(unittest.TestCase):
    def test_split_functions(self):
        self.assertEqual(
            split_array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4),
            [[1, 2, 3], [4, 5, 6], [7, 8], [9, 10]],
        )
        self.assertEqual(
            list(split_date_range("2015-01-01", "2015-02-28", 4)),
            ["2015-01-01", "2015-01-15", "2015-01-30", "2015-02-13", "2015-02-28"],
        )
        self.assertEqual(rreplace("anna@lox.com", "n", "", 1), "ana@lox.com")


class TestDecorators(unittest.TestCase):
    def test_perf_decorator(self):
        @Perf
        def perf_decor(x):
            return x * 2

        self.assertGreater(perf_decor(2), 0)


class TestSubstringFunctions(unittest.TestCase):
    def test_is_one_element_substring(self):
        value = "Alex_Mathis_Natasa"
        li_1 = ["Natasa", "Darian", "Melvil"]
        li_2 = ["Darian", "Melvil"]
        li_3 = ["Alex_Mathis_Natasa", "Darian_Melvil"]

        self.assertIs(is_one_element_substring(value, li_1, False), True)
        self.assertIs(is_one_element_substring(value, li_1, True), False)
        self.assertIs(is_one_element_substring(value, li_2), False)
        self.assertIs(is_one_element_substring(value, li_3, False), True)
        self.assertIs(is_one_element_substring(value, li_3, True), True)
