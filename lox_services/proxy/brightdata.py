import random
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import Callable, List

import requests

from lox_services.utils.decorators import DataUsage, Perf
from lox_services.utils.general_python import print_error, print_success

class BrightDataProxyManager:
    """Class that handles Bright Data proxy APIs."""
    
    def __init__(self, username, password, api_token):
        self.request_header = {
            'Authorization': f'Bearer {api_token}'
        }
        self.zones = ["data_center", "isp"]
        self.base_url = f"lum-customer-{username}-zone-{self.zones[0]}-ip-%s:{password}@zproxy.lum-superproxy.io:22225"
    
    ### PRIVATE ###
    
    @staticmethod
    def _handle_web_api_response(response: requests.Response):
        response_status = response.status_code
        if 200 <= response_status < 300:            
            return response.text
        else:
            error_message = f"{response_status} - {response.text}"
            print_error(error_message)
            raise Exception(f"Bright Data returned an error: {error_message}")
    
        
    @staticmethod
    def _excecute_request_with_retry(request_method: Callable, options: dict, retries: int = 2):
        result: requests.Response = request_method(**options)
        tries = 0
        while result.status_code >= 300 and tries < retries:
            tries += 1
            print_error(f"{tries} error occured, trying one more time.")
            time.sleep(1)
            result = request_method(**options)
        
        return result
    
    
    def _get_available_ips_per_countries(self, countries: List[str]):
        """Gets all available IPs per countries. Country Alpha-2 codes are working fine as parameters."""
        result = []
        for country in set(countries):
            response =  requests.get(
                url=f"https://luminati.io/api/zone/route_ips?zone={self.zones[0]}&country={country}",
                headers=self.request_header
            )
            ip_list = self._handle_web_api_response(response).split("\n")
            print_success(f"{len(ip_list)} IPs available for {country}.")
            result += ip_list
        
        print_success(f"{len(result)} IPs available for {len(countries)} countries.")
        return ip_list
    
    
    def _get_all_available_ips(self):
        """Gets all available IPs. Limited to 20k."""
        response =  requests.get(
            url=f"https://luminati.io/api/zone/route_ips?zone={self.zones[0]}",
            headers=self.request_header
        )
        ip_list = self._handle_web_api_response(response).split("\n")
        print_success(f"{len(ip_list)} IPs available.")
        return ip_list
    
    
    def _populate_proxies_into_request_options(
        self,
        request_options: List[dict],
        proxies: List[str],
        max_use_per_proxy: int = 1,
    ):
        # Generate the proxy option as accepted by requests package.
        proxies = list(map(lambda ip: {
            "http": f"http://{self.base_url % ip}", 
            "https": f"https://{self.base_url % ip}"
        }, proxies))
        
        # Populate the options
        use_single_proxy = 0
        for options in request_options:
            if use_single_proxy >= max_use_per_proxy:
                use_single_proxy = 0
            
            if use_single_proxy == 0:
                proxy_index = random.randint(0, len(proxies) - 1)

            use_single_proxy += 1
            options["proxies"] = proxies[proxy_index]
        
        return request_options
    
    ### END PRIVATE ###
    
    @Perf
    @DataUsage
    def request_with_multithreading_proxies(
        self,
        *,
        request_method: Callable,
        request_options: List[dict],
        countries: List[str] = ['NL'],
        max_use_per_proxy: int = 1,
        number_of_threads: int = 20,
    ) -> List[requests.Response]:
        """Executes many requests using proxies and multithreading for multiple countries.
            ## Arguments
            - `request_method`: Must be a requests method like requests.get ot requests.post or requests.put, etc...
            - `request_options`: The list of options to used by the request_method.
            - `countries`: A list of countries where the proxies should be.
            - `number_of_threads`: The number of threads to use.

            ## Returns
            - A list of requests.Response objects

            ## Examples
            ```python
            proxy_manager = BrightDataProxyManager(brightdata_username, brightdata_password, brightdata_api_token)
            test_ips = proxy_manager.request_with_multithreading_proxies(
                request_method=requests.get,
                request_options=[{"url": "https://api.ipify.org?format=json"} for _ in range(20)],
                countries=["FR", "NL"],
                number_of_threads=20
            )
            ```
        
        """
        proxies = self._get_available_ips_per_countries(countries) 
        options_with_proxies = self._populate_proxies_into_request_options(request_options, proxies, max_use_per_proxy)
        # options_with_proxies = request_options
        options_len = len(request_options)
        
        results = []
        with ThreadPoolExecutor(max_workers=number_of_threads) as executor:
            for result in executor.map(self._excecute_request_with_retry, repeat(request_method), options_with_proxies):
                if result.status_code == 200:
                    results.append(result)
                    if len(results) % int(options_len / 10) == 0:
                        print(f"{len(results)} / {options_len}")
                else:
                    print_error(result.status_code)
            
        return results
