import os
import pandas as pd
import unittest

from lox_services.pdf.reader import PDFtoCSV, PDFtoDf, convertListOfInchesToListOfPdfUnits, countNumberOfPagesOfPdf, inchesToPDFUnits

PDF_PATH = "lox_services/pdf/assets/XXXXXDXXXXXXXX.pdf"



class Test_encrypt_functions(unittest.TestCase):
    
    
    def test_convertListOfInchesToListOfPdfUnits(self):
        "All values in list must be multiplied by 72"
        list_of_inches = [1,1.5,2]
        final_list_of_inches = [72,108,144]
        self.assertEqual(convertListOfInchesToListOfPdfUnits(list_of_inches), final_list_of_inches)
    
    def test_load_key(self):
        'The number of page returned should be 1'
        number_of_page_in_the_pdf = 1
        self.assertEqual(countNumberOfPagesOfPdf(PDF_PATH),number_of_page_in_the_pdf)
        
        
    def test_inchesToPDFUnits(self):
        "All values must be multiplied by 72"
        initial_tuple = (1,1.5,2)
        final_tuple = (72,108,144) 
        self.assertEqual(inchesToPDFUnits(initial_tuple), final_tuple)
        
    def test_PDFtoCSV(self):
        'A CSV must be created in the same folder as the PDF file'
        first_page_to_read = 1
        area = [0, 10, 15, 20]
        columns = [0, 10, 15, 20]
        guess = True
        csv_file_created = PDFtoCSV(PDF_PATH, first_page_to_read, area, columns, guess)
        
        self.assertEqual(os.path.isfile(csv_file_created), True)
        
    def test_PDFtoDf(self):
        'A dataframe must be returned from the PDF file'
        first_page_to_read = 1
        last_page_to_read = 1
        area = []
        columns = []
        guess = False
        list_dataframe_created = PDFtoDf(PDF_PATH, first_page_to_read, last_page_to_read, area, columns, guess)

        self.assertEqual(isinstance(list_dataframe_created[0], pd.DataFrame), True)
