
import os
import unittest
import pandas as pd
from base64 import b64encode
from tempfile import NamedTemporaryFile
from lox_services.pdf.writer import save_pdf_from_base_64, dataframe_to_html_without_pandas_style, generate_pdf_file_from_dataframe
from pathlib import Path


class Test_writer_pdf_functions(unittest.TestCase):
    """
    A unit test class for the save_pdf_from_base_64 function.
    """
    def setUp(self):
        self.base_dir = os.path.join(
            os.path.dirname(__file__),
            "Files",
        )
        
        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)
            
    def test_save_pdf_from_base_64(self):
        # Case 1: Create a temporary file to save the PDF
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

        # Case 2: Raise an exception if the base64 data is not valid
        with self.assertRaises(ValueError):
            save_pdf_from_base_64("Not a base64 string", temp_file_path)
    
    def test_dataframe_to_html_without_pandas_style(self):
        
        html = dataframe_to_html_without_pandas_style(pd.DataFrame())
        self.assertIn("<tbody>", html)
        
    def test_generate_pdf_file_dataframe(self):
        
        # Case 1: From a dataframe
        pdf_path = os.path.join(self.base_dir, "test_df.pdf")
        generate_pdf_file_from_dataframe(pd.DataFrame(), pdf_path, False)
        
        self.assertTrue(os.path.exists(pdf_path))
        
        

if __name__ == "__main__":
    unittest.main()
