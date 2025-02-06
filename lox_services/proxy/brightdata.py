import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Sequence, Tuple
from tqdm import tqdm
import time
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

    def __init__(self, username, password, api_token, zone="data_center"):
        self.request_header = {"Authorization": f"Bearer {api_token}"}
        self.base_url_template = f"lum-customer-{username}-zone-{zone}-ip-%s:{password}@zproxy.lum-superproxy.io:22225"
        self.username = username
        self.password = password

    ### PRIVATE ###

    def _get_ip_list(self, country: str = None, zone: str = "data_center"):
        url = f"https://luminati.io/api/zone/route_ips?zone={zone}"
        if country:
            url += f"&country={country}"

        MAX_RETRIES = 3
        WAIT_TIME = 5  # seconds

        retry_count = 0
        while retry_count < MAX_RETRIES:
            response = requests.get(url=url, headers=self.request_header)
            response_status = response.status_code

            if 200 <= response_status < 300:
                return response.text.split("\n")
            elif response_status == 429:
                retry_count += 1
                time.sleep(WAIT_TIME)
            else:
                error_message = f"{response_status} - {response.text}"
                if error_message == "401 - Customer not found":
                    error_message = "Your BrightData API token is not up to date. Create or refresh it via https://brightdata.com/cp/setting. Then add the token to your .env file."
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

    def _get_available_ips_per_countries(
        self, countries: Sequence[str], zone: str = "data_center"
    ):
        """Gets all available IPs per countries. Country Alpha-2 codes are working fine as parameters."""
        result = []
        for country in set(countries):
            if AVAILABLE_IPS_PER_COUNTRY.get(country):
                print_success(f"Using cached IPs for {country}.")
                result += AVAILABLE_IPS_PER_COUNTRY.get(country)

            else:
                ip_list = self._get_ip_list(country, zone)
                AVAILABLE_IPS_PER_COUNTRY[country] = ip_list
                result += ip_list

        print_success(f"{len(result)} IPs available for {countries}.")
        return result

    def _get_all_available_ips(self):
        """Gets all available IPs. Limited to 20k."""
        ip_list = self._get_ip_list()
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
                    "http": f"http://{self.base_url_template % ip}",
                    "https": f"https://{self.base_url_template % ip}",
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

    def get_one_proxy(self, country: str = "US", zone: str = "data_center"):
        """Fetches a single proxy IP and returns the necessary proxy settings.

        Args:
            country (str): The country code to filter the proxy IPs.
            zone (str): The proxy type, either "data_center" or "residential" (default: "data_center").

        Returns:
            dict: A dictionary containing http and https proxies.

        Raises:
            Exception: If no proxy IP is available.
        """
        if zone not in ["data_center", "isp"]:
            raise ValueError("Zone must be either 'data_center' or 'residential'")

        proxy_list = self._get_ip_list(country=country, zone=zone)
        if not proxy_list:
            raise Exception(
                "No proxy IP available. Check your proxy manager configuration."
            )

        proxy_ip = random.choice(proxy_list)
        proxy_url = (
            self.base_url_template.format(
                username=self.username, zone=zone, password=self.password
            )
            % proxy_ip
        )
        proxies = {
            "http": f"http://{proxy_url}",
            "https": f"https://{proxy_url}",
        }
        print(f"Using {zone} proxy IP: {proxy_ip}")
        return proxies

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
        show_progress: bool = False,
    ) -> List[requests.Response]:
        """Executes many requests using proxies and multithreading for multiple countries.
        ## Arguments
        - `request_method`: Must be a requests method like requests.get ot requests.post or requests.put, etc...
        - `request_options`: The list of options to used by the request_method.
        - `countries`: A list of countries where the proxies should be.
        - `number_of_threads`: The number of threads to use.
        - `max_use_per_proxy`: The maximum number of use per ip for this call.
        - `show_progress`: If True, the function will print a pretty progress bar.

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
        if show_progress:
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

    @Perf
    def function_with_multithreading_proxies(
        self,
        *,
        request_method: Callable,
        request_options: Sequence[dict],
        countries: Sequence[str] = ("NL",),
        number_of_threads: int = 25,
        max_use_per_proxy: int = 10,
        show_progress: bool = False,
        zone: str = "data_center",
    ) -> Tuple[List[requests.Response], List[str]]:
        """Executes many requests using proxies and multithreading for multiple countries.
        ## Arguments
        - `request_method`: Must be a requests method like requests.get ot requests.post or requests.put, etc...
        - `request_options`: The list of options to used by the request_method.
        - `countries`: A list of countries where the proxies should be.
        - `number_of_threads`: The number of threads to use.
        - `max_use_per_proxy`: The maximum number of use per ip for this call.
        - `show_progress`: If True, the function will print a pretty progress bar.

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
        responses_list = []
        tracking_numbers_list = []

        number_of_threads = min(50, number_of_threads)
        proxies = self._get_available_ips_per_countries(countries, zone)
        options_with_proxies = self._populate_proxies_into_request_options(
            request_options, proxies, max_use_per_proxy
        )

        options_len = len(options_with_proxies)
        progress_bar = tqdm(total=options_len)
        # The right way to add a progress bar with multithreading -
        # https://stackoverflow.com/a/63834834
        results = []
        options_len = len(options_with_proxies)
        with ThreadPoolExecutor(max_workers=number_of_threads) as executor:
            futures = [
                executor.submit(lambda option=option: request_method(**option))
                for option in options_with_proxies
            ]
            for future in as_completed(futures):
                results.append(future.result())
                progress_bar.update()
        progress_bar.close()

        for item in results:
            responses_list.extend(item["responses"])
            tracking_numbers_list.extend(item["tracking_numbers"])

        return responses_list, tracking_numbers_list
