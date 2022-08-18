from os.path import join, dirname


BILLING_ASSETS_FOLDER = join(dirname(__file__), "assets")

#10 € minimum to invoice a customer, otherwise customer is skipped this month
MIN_INVOICING_AMOUNT = 10

ACCOUNTANT_EMAIL = "syfers.6285@mailsyfers.nl"
LOX_CC_EMAIL = "dylan.hirsch@loxsolution.com"
LOX_FR_CC_EMAIL = "isis.fordant@loxsolution.com"

MANDATORY_BILLING_FIELDS = [
    "company",
    "country",
    "vat",
    "invoicing_emails",
    "auto_email",
]