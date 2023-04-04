from enum import Enum


class TranslationModules(Enum):
    """Enumeration of the Lox translation modules."""

    ROOT = ""
    BILLING_INVOICE = "billing/invoice"
    BILLING_EMAIL = "billing/email"
