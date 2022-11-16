import unittest

from lox_services.pdf.reader import countNumberOfPagesOfPdf, inchesToPDFUnits

PDF_PATH = "lox_services/pdf/XXXXXDXXXXXXXX.pdf"



class Test_encrypt_functions(unittest.TestCase):
    
    def test_load_key(self):
        self.assertEqual(countNumberOfPagesOfPdf(PDF_PATH),1)
        
        
    def test_inchesToPDFUnits(self):
        "All values must be multiplied by 72"
        initial_tuple = (1,1.5,2)
        final_tuple = (72,108,144) 
        self.assertEqual(inchesToPDFUnits(initial_tuple), final_tuple)