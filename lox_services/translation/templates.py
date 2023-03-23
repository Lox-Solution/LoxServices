from typing import Dict


def insert_variables(translations: Dict[str, str], **kwargs):
    """Insert multiple variables in the dictionnary of translations.
    ## Arguments
        - `translations`: The dictionnary of translations.
        - `kwargs`: The variables to insert.

    ## Example
        >>> translations_with_variables = insert_variables(
                {
                    "subject": "Lox Invoice - {company}: {month} {year}",
                    "title": "Lox Invoice - {month} {year}",
                    "entrance_greetings": "Dear {company},"
                },
                company= "Lox",
                month= "March",
                year= "2022",
            )
        # {
        #   'subject': 'Lox Invoice - Lox: March 2022',
        #   'title': 'Lox Invoice - March 2022',
        #   'entrance_greetings': 'Dear Lox,'
        # }
    """
    new_translations = {}
    for key, value in translations.items():
        for variable_name, variable_value in kwargs.items():
            value = str(value).replace(f"{{{variable_name}}}", str(variable_value))
        new_translations[key] = value

    return new_translations
