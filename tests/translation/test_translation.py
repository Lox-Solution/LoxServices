import json
import os
import unittest

from lox_services.translation.translate import get_translations
from lox_services.translation.templates import insert_variables
from lox_services.utils import json_file_to_python_dictionary


service_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "lox_services", "translation", "languages")
json_path_and_length = {'/': 12, '/billing/email/': 11, '/billing/invoice/': 20}

class Test_translation_files(unittest.TestCase):
    
    def test_translation_file_length(self):
        """Checks that number of keys hasn't changed"""
        for path, length in json_path_and_length.items():
            file_list = [f for f in os.listdir(service_path + path)if f.endswith('.json')]
            for file in file_list:
                file_data = json_file_to_python_dictionary(service_path + path + file)
                assert len(file_data) == length
                    
                    
    def test_translation_file_keys(self):
        """Checks that keys match in all languages"""
        for json_path in json_path_and_length:
            json_list = [f for f in os.listdir(service_path + json_path)if f.endswith('.json')]
            english_dictionary = json_file_to_python_dictionary(service_path + json_path + 'EN.json')
            for json_file in json_list:
                dictionary = json_file_to_python_dictionary(service_path + json_path + json_file)
                assert english_dictionary.keys() == dictionary.keys()
        
    def test_get_translation_exception(self):
        self.assertRaises(Exception, get_translations, "NL", True)
        
        
        
email_en = {
    "subject": "Lox Invoice - {company}: {month} {year}"
}

email_en_with_variables = {
    "subject": "Lox Invoice - Helloprint: September 2022"
}

invoice_fr = {
    "t_title": "Facture Lox Solution - {invoice_date}",
    "t_recap_sentence": "Veuillez transférer le montant <strong>{total_with_vat}</strong> avant le: <strong>{invoice_due_date}</strong> au nom de LOX SOLUTION B.V.  sur le compte bancaire: <strong>NL35 BUNQ 2045 1979 72</strong> avec la référence de facture: {invoice_number}",
}

invoice_fr_with_variables = {
    "t_title": "Facture Lox Solution - 22/06/2022",
    "t_recap_sentence": "Veuillez transférer le montant <strong>7300€</strong> avant le: <strong>15/07/2022</strong> au nom de LOX SOLUTION B.V.  sur le compte bancaire: <strong>NL35 BUNQ 2045 1979 72</strong> avec la référence de facture: 1234567890",
}
    
class Test_insert_variables(unittest.TestCase):
    
    def test_translations_with_variables(self):
        self.assertDictEqual(insert_variables(email_en, company = 'Helloprint', month = 'September', year = '2022'), email_en_with_variables)
        self.assertDictEqual(insert_variables(invoice_fr, invoice_date = '22/06/2022', total_with_vat = '7300€', invoice_due_date = '15/07/2022', invoice_number = '1234567890'), invoice_fr_with_variables)


