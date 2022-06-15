import re # You may need this
from typing import List


# Good to take a look at this: https://help.returnpath.com/hc/en-us/articles/220560587-What-are-the-rules-for-email-address-syntax-
def extract_emails_from_string(string: str) -> List[str]:
    """Extracts all emails from a string.
        ## Arguments
        - `string`: The string to extract emails from.
        
        ## Returns
        - A list of emails if any were found.
        - An empty list if no emails were found.    

        ## Examples
        ```
            emails = extract_emails_from_string("My email is alexandre@domain.com")
            print(emails) # ["alexandre@domain.com"]
            
            no_emails = extract_emails_from_string("This is a string without emails")
            print(no_emails) # []
        ```
    """

    return re.findall(r"[a-zA-z0-9!#$%&*+-/=?^_`}{|]+@[a-zA-z0-9.-]+\.[a-zA-z0-9-]+", string)
