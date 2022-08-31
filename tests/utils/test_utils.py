import os
import unittest
import datetime

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
    split_date_range)


SERVICE_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
file_path = os.path.join(SERVICE_PATH, 'setup.py')


class Test_files_and_folders_functions(unittest.TestCase):
    
    def test_is_file_or_folder_path(self):
        self.assertEqual(is_file_or_folder_path(file_path),'file')
        self.assertNotEqual(is_file_or_folder_path(file_path),'folder')
        self.assertEqual(is_file_or_folder_path(SERVICE_PATH),'folder')
        self.assertNotEqual(is_file_or_folder_path(SERVICE_PATH),'file')
        self.assertRaises(ValueError, is_file_or_folder_path, os.path.join(SERVICE_PATH, '//setup.py'))
        
    def test_get_file_or_folder_size(self):
        self.assertGreaterEqual(get_file_size(os.path.join(SERVICE_PATH, 'CHANGELOG.md')), (379.0, 'BYTES'))
        self.assertNotEqual(get_file_size(os.path.join(SERVICE_PATH, 'CHANGELOG.md')), (0, 'BYTES'))
        self.assertGreaterEqual(get_folder_size(os.path.join(SERVICE_PATH, 'lox_services')), (322.64, 'KB'))
        self.assertNotEqual(get_folder_size(os.path.join(SERVICE_PATH, 'lox_services')), (0, 'KB'))

        
class Test_convert_and_format_functions(unittest.TestCase):
    
    def test_convert_functions(self):
        self.assertEqual(convert_bytes_to_human_readable_size_unit(12345), (12.06, 'KB'))
        self.assertEqual(convert_date_with_foreign_month_name('2022', 'feb', '21'), datetime.datetime(2022, 2, 21, 0, 0))
        
    def test_format_functions(self):
        self.assertEqual(format_snake_case_to_human_upper_case('hello_world'), 'Hello World')
        self.assertEqual(format_amount_to_human_string('120050.10', 'EN', '€'), '€120,050.10 ')
        self.assertEqual(format_amount_to_human_string('120050.10', 'FR', '$'), '120,050.10 $')
        
        
class Test_split_and_replace_functions(unittest.TestCase):
    
    def test_split_functions(self):
        self.assertEqual(split_array([1,2,3,4,5,6,7,8,9,10], 4), [[1, 2, 3], [4, 5, 6], [7, 8], [9, 10]])
        self.assertEqual(list(split_date_range('2015-01-01', '2015-02-28', 4)),['2015-01-01', '2015-01-15', '2015-01-30', '2015-02-13', '2015-02-28'])
        self.assertEqual(rreplace('l_team@l_solution.com', '_', 'ox', 2), 'loxteam@loxsolution.com')

