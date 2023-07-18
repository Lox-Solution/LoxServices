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
from tests import OUTPUT_FOLDER


class Test_pdf_functions(unittest.TestCase):
    def setUp(self):
        self.pdf_path = os.path.join(OUTPUT_FOLDER, "XXXXXDXXXXXXXX.pdf")

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
        self.assertEqual(
            countNumberOfPagesOfPdf(self.pdf_path), number_of_page_in_the_pdf
        )

    def test_inchesToPDFUnits(self):
        "All values must be multiplied by 72"
        initial_tuple = (1, 1.5, 2)
        final_tuple = (72, 108, 144)
        self.assertEqual(inchesToPDFUnits(initial_tuple), final_tuple)

    def test_PDFtoCSV(self):
        path_to_pdf = self.pdf_path
        first_page_to_read = 1
        area = []
        columns = []
        guess = True

        expected_csv_path = path_to_pdf.replace(".pdf", ".csv")

        csv_path = PDFtoCSV(path_to_pdf, first_page_to_read, area, columns, guess)
        self.assertEqual(
            csv_path, expected_csv_path
        )  # Check if the returned CSV path is correct
        dataframe_from_pdf = pd.read_csv(csv_path, header=None)

        self.assertTrue(
            any(
                "alice" in str(row[0]).lower()
                for _, row in dataframe_from_pdf.iterrows()
            ),
            "The first column does not contain the word 'Alice'.",
        )

    def test_PDFtoDf(self):
        "A List of dataframe must be returned from the PDF file"

        # Case 1: area is a list of 4 elements
        list_dataframe_created = PDFtoDf(
            self.pdf_path,
            first_page_to_read=1,
            last_page_to_read=1,
            area=[],
            columns=[],
            guess=False,
        )
        self.assertEqual(
            all(isinstance(x, pd.DataFrame) for x in list_dataframe_created), True
        )
        self.assertTrue(
            any(
                "alice" in str(row[0]).lower()
                for _, row in list_dataframe_created[0].iterrows()
            ),
            "The first column does not contain the word 'Alice'.",
        )

        # Case 2: area is a list of 4 lists
        list_dataframe_created = PDFtoDf(
            self.pdf_path,
            first_page_to_read=1,
            last_page_to_read=None,
            area=[],
            columns=[],
            guess=True,
        )
        self.assertEqual(
            all(isinstance(x, pd.DataFrame) for x in list_dataframe_created), True
        )
        self.assertTrue(
            any(
                "alice" in str(row[0]).lower()
                for _, row in list_dataframe_created[0].iterrows()
            ),
            "The first column does not contain the word 'Alice'.",
        )

    def test_is_word_in_pdf(self):
        "True must be returned when the word is present in the dataframe, False otherwise"

        word_existing_in_pdf = "Alice"
        word_non_existing_in_pdf = "Hello world"
        self.assertEqual(
            is_word_in_pdf(self.pdf_path, 1, 1, word_existing_in_pdf), True
        )
        self.assertEqual(
            is_word_in_pdf(self.pdf_path, 1, 1, word_non_existing_in_pdf), False
        )


if __name__ == "__main__":
    unittest.main()
