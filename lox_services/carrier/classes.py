from abc import ABC, abstractmethod
from typing import Dict

class WrongCredentialsException(Exception):
    """Raised when the combination username/password is incorrect.
        It updates the `is_wrong_credentials` attribute in database to avoid doing the run again.
    """
    
    def __str__(self):
        return "WrongCredentialsException"


class CredentialsChecker(ABC):
    """Abstract class for checking carriers credentials"""

    @abstractmethod
    def check_credentials(self, credentials: Dict):
        """Useses Selenium and Xvfb to check credentials."""
        try: 
            self._login(credentials)
        except WrongCredentialsException:
            return False
        
        return True
        
    
    @abstractmethod
    def get_average_compute_time(self):
        """Gets the hard-coded average compute time for the carrier (in seconds)."""
        pass
