import gzip
import os
import re
import unittest
from lox_services.utils.formats import (
    json_file_to_python_dictionary,
    image_to_base64,
    gzip_to_csv,
)


class TestConversionFunctions(unittest.TestCase):
    def setUp(self):
        """Set up the base directory of your repository."""
        self.base_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "Files"
        )
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def test_json_file_to_python_dictionary(self):
        # Define the relative path to the test JSON file
        file_path = os.path.join(self.base_dir, "test.json")
        json_data = '{"key1": "value1", "key2": "value2"}'

        # Create the test JSON file
        with open(file_path, "w") as file:
            file.write(json_data)

        # Call the function
        result = json_file_to_python_dictionary(file_path)

        # Assertions
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})

        os.remove(file_path)

    def test_image_to_base64(self):
        # Define the relative path to the test image file
        image_path = os.path.join(self.base_dir, "test_image.png")

        # Call the function
        result = image_to_base64(image_path)

        # Assertions
        self.assertIsInstance(result, str)
        print(result)

        """Check if a string is Base64 encoded."""
        # https://stackoverflow.com/questions/8571501/how-to-check-whether-a-string-is-base64-encoded-or-not
        pattern = r"^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$"
        return bool(re.match(pattern, result))

    def test_gzip_to_csv(self):
        # Define the relative paths to the test input and output files
        infile = os.path.join(self.base_dir, "test_input.csv.gz")
        compressed_data = gzip.compress(b"test data")

        # Create the test input file
        with open(infile, "wb") as file:
            file.write(compressed_data)

        # Define the relative path to the test output file
        tofile = os.path.join(self.base_dir, "test_output.csv")

        # Call the function
        gzip_to_csv(infile, tofile)

        # Read the output file contents
        with open(tofile, "r") as file:
            result = file.read()

        # Assertions
        self.assertIsInstance(result, str)
        self.assertEqual(result, "test data")

        os.remove(infile)

        os.remove(tofile)


if __name__ == "__main__":
    unittest.main()
