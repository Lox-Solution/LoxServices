import json
import os
import unittest

from lox_services.translation.translate import get_translations
from lox_services.translation.templates import insert_variables


service_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "lox_services", "translation")

class Test_translation_files(unittest.TestCase):
    
    def test_translation_file_length(self):
        """Checks that number of keys hasn't changed"""
        file_path_and_length = {'/languages/': 12, '/languages/billing/email/': 11, '/languages/billing/invoice/': 20}
        for path, length in file_path_and_length.items():
            file_list = [f for f in os.listdir(service_path + path)if f.endswith('.json')]
            for file in file_list:
                with open(service_path + path + file) as file:
                    file_data = json.load(file)
                    assert len(file_data) == length
                    
                    
    def test_translation_file_keys(self):
        """Checks that keys match in all languages"""
        json_file_paths = ['/languages/', '/languages/billing/email/', '/languages/billing/invoice/']
        for json_path in json_file_paths:
            json_list = [f for f in os.listdir(service_path + json_path)if f.endswith('.json')]
            english_json = json.load(open(service_path + json_path + 'EN.json'))
            for json_file in json_list:
                with open(service_path + json_path + json_file) as json_file:
                    json_data = json.load(json_file)
                    assert english_json.keys() == json_data.keys()
                    self.assertEqual(english_json.keys(), json_data.keys())
        
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


