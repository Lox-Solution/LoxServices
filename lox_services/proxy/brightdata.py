import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Sequence
from tqdm import tqdm

import requests
import urllib3

from lox_services.utils.decorators import DataUsage, Perf
from lox_services.utils.general_python import print_error, print_success

AVAILABLE_IPS_PER_COUNTRY = (
    {}
)  # Used to cache the available IPs per country. This is used to avoid calling
# the BrightData API too often (otherwise error 429 are returned).


class BrightDataProxyManager:
    """Class that handles Bright Data proxy APIs."""

    def __init__(
        self, username: str, password: str, api_token: str, show_progress: bool = False
    ):
        self.request_header = {"Authorization": f"Bearer {api_token}"}
        self.zones = ["data_center", "isp"]
        self.base_url = f"lum-customer-{username}-zone-{self.zones[0]}-ip-%s:{password}@zproxy.lum-superproxy.io:22225"
        self.show_progress = show_progress

    ### PRIVATE ###

    @staticmethod
    def _handle_web_api_response(response: requests.Response):
        response_status = response.status_code
        if 200 <= response_status < 300:
            return response.text
        else:
            error_message = f"{response_status} - {response.text}"
            if error_message == "401 - Customer not found":
                error_message = (
                    "Your BrightData API token is not up to date. Create or refresh it via "
                    "https://brightdata.com/cp/setting. Then add the token to your .env file."
                )
            print_error(error_message)
            raise Exception(f"Bright Data returned an error: {error_message}")

    @staticmethod
    def _excecute_request_with_retry(
        request_method: Callable, options: dict, retries: int = 3
    ):

        tries = 0
        result = requests.Response
        result.status_code = 300

        while result.status_code >= 300 and tries < retries:

            try:
                result = request_method(**options)

            except requests.exceptions.ProxyError as error:
                for arg in error.args:
                    if isinstance(arg, urllib3.exceptions.MaxRetryError):
                        if "407 Auth Failed (code: ip_forbidden)" in str(
                            arg.reason.original_error
                        ):
                            raise Exception(
                                "BrightData needs to whitelist your IP address. Please contact Melvil."
                            ) from error

                result.status_code = 407

            except requests.exceptions.SSLError:
                result.status_code = 407

            ip = options["proxies"]["http"].split("ip-")[1].split(":")[0]

            if result.status_code == 403:
                print_error(f"403 Forbidden with ip: {ip}.")
            elif result.status_code == 407:
                print_error(f"407 Proxy connection error with ip: {ip}.")
            elif result.status_code == 443:
                print_error(f"443 blocked with ip: {ip}.")
            elif result.status_code >= 300:
                print_error(f"{result.status_code} status code with ip: {ip}.")

            if tries > 0:
                print_error(
                    f"{ip}: {tries} error(s) occured (status code {result.status_code}), trying one more time."
                )

            tries += 1

        return result

    def _get_available_ips_per_countries(self, countries: Sequence[str]):
        """Gets all available IPs per countries. Country Alpha-2 codes are working fine as parameters."""
        result = []
        for country in set(countries):
            if AVAILABLE_IPS_PER_COUNTRY.get(country):
                if not self.show_progress:
                    print_success(f"Using cached IPs for {country}.")
                result += AVAILABLE_IPS_PER_COUNTRY.get(country)

            else:
                response = requests.get(
                    url=f"https://luminati.io/api/zone/route_ips?zone={self.zones[0]}&country={country}",
                    headers=self.request_header,
                )
                ip_list = self._handle_web_api_response(response).split("\n")
                AVAILABLE_IPS_PER_COUNTRY[country] = ip_list
                result += ip_list
        if not self.show_progress:
            print_success(f"{len(result)} IPs available for {countries}.")
        return result

    def _get_all_available_ips(self):
        """Gets all available IPs. Limited to 20k."""
        response = requests.get(
            url=f"https://luminati.io/api/zone/route_ips?zone={self.zones[0]}",
            headers=self.request_header,
        )
        ip_list = self._handle_web_api_response(response).split("\n")
        print_success(f"{len(ip_list)} IPs available.")
        return ip_list

    def _populate_proxies_into_request_options(
        self,
        request_options: Sequence[dict],
        proxies: Sequence[str],
        max_use_per_proxy: int = 1,
    ):
        # Generate the proxy option as accepted by requests package.
        proxies = list(
            map(
                lambda ip: {
                    "http": f"http://{self.base_url % ip}",
                    "https": f"https://{self.base_url % ip}",
                },
                proxies,
            )
        )

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
        request_options: Sequence[dict],
        countries: Sequence[str] = ("NL",),
        number_of_threads: int = 25,
        max_use_per_proxy: int = 10,
    ) -> List[requests.Response]:
        """Executes many requests using proxies and multithreading for multiple countries.
        ## Arguments
        - `request_method`: Must be a requests method like requests.get ot requests.post or requests.put, etc...
        - `request_options`: The list of options to used by the request_method.
        - `countries`: A list of countries where the proxies should be.
        - `number_of_threads`: The number of threads to use.
        - `max_use_per_proxy`: The maximum number of use per ip for this call.

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
        number_of_threads = min(50, number_of_threads)
        proxies = self._get_available_ips_per_countries(countries)
        options_with_proxies = self._populate_proxies_into_request_options(
            request_options, proxies, max_use_per_proxy
        )

        # The right way to add a progress bar with multithreading -
        # https://stackoverflow.com/a/63834834
        results = []
        options_len = len(options_with_proxies)
        if self.show_progress:
            progress_bar = tqdm(total=options_len)
            with ThreadPoolExecutor(max_workers=number_of_threads) as executor:
                futures = [
                    executor.submit(
                        self._excecute_request_with_retry, request_method, option
                    )
                    for option in options_with_proxies
                ]
                for future in as_completed(futures):
                    results.append(future.result())
                    progress_bar.update()
            progress_bar.close()
        else:
            with ThreadPoolExecutor(max_workers=number_of_threads) as executor:
                futures = [
                    executor.submit(
                        self._excecute_request_with_retry, request_method, option
                    )
                    for option in options_with_proxies
                ]
                for future in as_completed(futures):
                    results.append(future.result())
        return results
