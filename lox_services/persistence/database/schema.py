"""Contains the types of some table fields of the database."""

dtypes_invoices = {
    'company': str,
    'carrier': str,
    'account_number': str,
    'invoice_number': str,
    'invoice_date': str,
    'reference': str,
    'tracking_number': str,
    'url': str,
    'description': str,
    'quantity': int,
    'amount': float,
    'incentive_amount': float,
    'net_amount': float,
    'discount': float,
    'country_code_sender': str,
    'country_code_receiver': str,
    'postal_code_receiver': str,
    'type_charges': str,
    'weight': float,
    'length': float,
    'width': float,
    'height': float,
    'zone': str,
    # 'type_weight': str,
    # missing in the csv
    # 'lead_tracking_number': str,
    # 'is_return': bool
}

na_invoices = {
    'company': '',
    'carrier': '',
    'account_number': '',
    'invoice_number': '',
    'reference': '',
    'tracking_number': '',
    'url': '',
    'description': '',
    'quantity': 1,
    'amount': 0.0,
    'incentive_amount': 0.0,
    'net_amount': 0.0,
    'discount': 0.0,
    'country_code_sender': '',
    'country_code_receiver': '',
    'postal_code_receiver': '',
    'type_charges': '',
    'weight': 0.0,
    'length': 0.0,
    'width': 0.0,
    'height': 0.0,
    'type_weight': '',
    'zone': '',
    'lead_tracking_number': '',
    'is_return': False
}

dates_invoices= ['invoice_date']
    
dtypes_deliveries = {
    'tracking_number': str,
    'alternative_tracking_number': str,
    'status': str,
    'final_status': str,
    'location': str,
    'number_packages': int,
    'is_return': bool,
    'url': str
}
na_deliveries = {
    'alternative_tracking_number': '',
    'final_status': '',
    'is_return': False,
    'location': '',
    'number_packages': 1,
    'status': '',
    'time': '00:00:00',
    'tracking_number': '',
    'url': ''
}

dates_deliveries = ['date']

dtypes_refunds = {
    'company': str,
    'carrier': str,
    'invoice_number': str,
    'invoice_date': str,
    'refund_invoice_number': str,
    'refund_invoice_date': str,
    'reference': str,
    'service_level': str,
    'tracking_number': str,
    'total_price': float,
    'reason_refund': str,
    'real_weight': float,
    'real_size': str,
    'url': str,
    'state': str,
    'status': str,
    'request_open_days': int,
    'request_date': str,
    'confirm_date': str,
    'credit_date': str,
    'declined_date': str,
    'reminder_date_01': str,
    'reminder_date_02': str,
    'last_contact_date': str,
    # missing in the csv
    # 'credit_invoice_number': str,
    # 'lox_invoice_number': str,
    # 'claim_number': str,
    # 'is_lox_claim': bool,
    # 'dispute_date': str
}

na_refunds = {
    'company': '',
    'carrier': '',
    'invoice_number': '',
    'invoice_date': '',
    'refund_invoice_number': '',
    'refund_invoice_date': '',
    'url': '',
    'reason_refund': '',
    'total_price': 0.0,
    'tracking_number': '',
    'reference': '',
    'service_level': '',
    'real_weight': 0.0,
    'real_size': '',
    'state': '',
    'status': '',
    'request_open_days': 0,
    'credit_invoice_number': '',
    'lox_invoice_number': '',
    'claim_number': '',
    'is_lox_claim': False,
    'request_date': '',
    'confirm_date': '',
    'credit_date': '',
    'declined_date': '',
    'reminder_date_01': '',
    'reminder_date_02': '',
    'last_contact_date': '',
    'dispute_date': '',
}

dates_refunds = [
    'invoice_date',
    'request_date',
    'confirm_date',
    'credit_date',
    'declined_date',
    'reminder_date_01',
    'reminder_date_02',
    'last_contact_date',
    # 'dispute_date',
]
