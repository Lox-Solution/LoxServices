import os
import unittest

from lox_services.translation.translate import get_translations
from lox_services.translation.templates import insert_variables
from lox_services.utils import json_file_to_python_dictionary


SERVICE_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "lox_services", "translation", "languages")
JSON_PATHS = ['', 'billing/email', 'billing/invoice']

class Test_translation_files(unittest.TestCase):
    
    def test_translation_file_keys(self):
        """Checks that keys match in all languages"""
        for path in JSON_PATHS:
            module_path = os.path.join(SERVICE_PATH, path)
            json_list = [f for f in os.listdir(module_path)if f.endswith('.json')]
            english_dictionary = json_file_to_python_dictionary(os.path.join(module_path, 'EN.json'))
            for json_file in json_list:
                file_path = os.path.join(module_path, json_file)
                dictionary = json_file_to_python_dictionary(file_path)
                assert english_dictionary.keys() == dictionary.keys(), file_path
        
    def test_get_translation_exception(self):
        self.assertRaises(Exception, get_translations, "NL", True)
        
        
        
mock_email_en = {
    "subject": "Lox Invoice - {company}: {month} {year}"
}

mock_email_en_with_variables = {
    "subject": "Lox Invoice - Helloprint: September 2022"
}

mock_invoice_fr = {
    "t_title": "Facture Lox Solution - {invoice_date}",
    "t_recap_sentence": "Veuillez transférer le montant <strong>{total_with_vat}</strong> avant le: <strong>{invoice_due_date}</strong> au nom de LOX SOLUTION B.V.  sur le compte bancaire: <strong>NL35 BUNQ 2045 1979 72</strong> avec la référence de facture: {invoice_number}",
}

mock_invoice_fr_with_variables = {
    "t_title": "Facture Lox Solution - 22/06/2022",
    "t_recap_sentence": "Veuillez transférer le montant <strong>7300€</strong> avant le: <strong>15/07/2022</strong> au nom de LOX SOLUTION B.V.  sur le compte bancaire: <strong>NL35 BUNQ 2045 1979 72</strong> avec la référence de facture: 1234567890",
}
    
class Test_insert_variables(unittest.TestCase):
    
    def test_translations_with_variables(self):
        self.assertDictEqual(insert_variables(mock_email_en, company = 'Helloprint', month = 'September', year = '2022'), mock_email_en_with_variables)
        self.assertDictEqual(insert_variables(mock_invoice_fr, invoice_date = '22/06/2022', total_with_vat = '7300€', invoice_due_date = '15/07/2022', invoice_number = '1234567890'), mock_invoice_fr_with_variables)


