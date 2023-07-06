import unittest

from base64 import b64encode
from tempfile import NamedTemporaryFile
from lox_services.pdf.writer import save_pdf_from_base_64
from pathlib import Path


class Test_writer_pdf_functions(unittest.TestCase):
    """
    A unit test class for the save_pdf_from_base_64 function.
    """

    def test_save_pdf_from_base_64(self):
        """
        Test the save_pdf_from_base_64 function.

        This test case generates a Base64 string,
        calls the function to save the PDF, and asserts that the saved file contents
        match the original sample PDF content.
        """
        pdf_data = b"%PDFDummyPDFContent"
        base64_data = b64encode(pdf_data).decode()

        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        save_pdf_from_base_64(base64_data, temp_file_path)

        self.assertTrue(Path(temp_file_path).exists())

        with open(temp_file_path, "rb") as saved_file:
            saved_data = saved_file.read()
            self.assertEqual(saved_data, pdf_data)

        # Clean up the temporary file
        Path(temp_file_path).unlink()


if __name__ == "__main__":
    unittest.main()
