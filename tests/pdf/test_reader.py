import os
import pandas as pd
import unittest
from unittest.mock import patch
from typing import List
import tabula

from lox_services.pdf.reader import (
    PDFtoDf,
    PDFtoCSV,
    convertListOfInchesToListOfPdfUnits,
    countNumberOfPagesOfPdf,
    inchesToPDFUnits,
    is_word_in_pdf,
)

PDF_PATH = os.path.join(os.path.dirname(__file__), "XXXXXDXXXXXXXX.pdf")


class Test_pdf_functions(unittest.TestCase):
    def test_convertListOfInchesToListOfPdfUnits(self):
        "All values in list must be multiplied by 72"
        list_of_inches = [1, 1.5, 2]
        final_list_of_inches = [72, 108, 144]
        self.assertEqual(
            convertListOfInchesToListOfPdfUnits(list_of_inches), final_list_of_inches
        )

    def test_number_of_pages(self):
        "The number of page returned should be 1"
        number_of_page_in_the_pdf = 1
        self.assertEqual(countNumberOfPagesOfPdf(PDF_PATH), number_of_page_in_the_pdf)

    def test_inchesToPDFUnits(self):
        "All values must be multiplied by 72"
        initial_tuple = (1, 1.5, 2)
        final_tuple = (72, 108, 144)
        self.assertEqual(inchesToPDFUnits(initial_tuple), final_tuple)

    def test_PDFtoCSV(self, mock_convert_into, mock_countNumberOfPagesOfPdf):
        mock_countNumberOfPagesOfPdf.return_value = (
            5  # Mocking the return value of countNumberOfPagesOfPdf
        )
        path_to_pdf = PDF_PATH
        first_page_to_read = 2
        area = [10, 20, 30, 40]
        columns = [0.1, 0.2, 0.3]
        guess = True

        expected_csv_path = path_to_pdf.replace(".pdf", ".csv")

        csv_path = PDFtoCSV(path_to_pdf, first_page_to_read, area, columns, guess)

        self.assertEqual(
            csv_path, expected_csv_path
        )  # Check if the returned CSV path is correct
        mock_countNumberOfPagesOfPdf.assert_called_once_with(
            path_to_pdf
        )  # Check if countNumberOfPagesOfPdf was called with the correct argument
        mock_convert_into.assert_called_once_with(
            path_to_pdf,
            output_path=expected_csv_path,
            pages="2-5",
            area=area,
            columns=columns,
            guess=guess,
        )  # Check if convert_into was called with the correct arguments

    def test_PDFtoDf(self):
        "A List of dataframe must be returned from the PDF file"
        first_page_to_read = 1
        last_page_to_read = 1
        area = []
        columns = []
        guess = False
        list_dataframe_created = PDFtoDf(
            PDF_PATH, first_page_to_read, last_page_to_read, area, columns, guess
        )
        self.assertEqual(
            all(isinstance(x, pd.DataFrame) for x in list_dataframe_created), True
        )

    def test_is_word_in_pdf(self):
        "True must be returned when the word is present in the dataframe, False otherwise"

        word_existing_in_pdf = "Invoice 71344294"
        word_non_existing_in_pdf = "Hello world"
        self.assertEqual(is_word_in_pdf(PDF_PATH, 1, 1, word_existing_in_pdf), True)
        self.assertEqual(
            is_word_in_pdf(PDF_PATH, 1, 1, word_non_existing_in_pdf), False
        )


if __name__ == "__main__":
    unittest.main()
