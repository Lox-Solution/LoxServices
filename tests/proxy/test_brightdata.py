from typing import List, Tuple
import unittest
import random
import requests
from lox_services.proxy.brightdata import BrightDataProxyManager
from lox_services.config.env_variables import get_env_variable


class TestBrightDataProxyManager(unittest.TestCase):
    def setUp(self):
        self.username = get_env_variable("BRIGHTDATA_USERNAME")
        self.password = get_env_variable("BRIGHTDATA_PASSWORD")
        self.api_token = get_env_variable("BRIGHTDATA_API_TOKEN")
        self.proxy_manager = BrightDataProxyManager(
            self.username, self.password, self.api_token
        )

    def test_request_with_multithreading_proxies(self):
        # Define request options
        request_options = [
            {"url": "https://www.example.com"},
            {"url": "https://www.google.com"},
            {"url": "https://www.openai.com"},
        ]

        # Call the function
        responses = self.proxy_manager.request_with_multithreading_proxies(
            request_method=requests.get,
            request_options=request_options,
            countries=["NL", "FR"],
            number_of_threads=5,
            max_use_per_proxy=3,
            show_progress=True,
        )

        # Assertions
        self.assertEqual(len(responses), len(request_options))
        for response in responses:
            self.assertIsInstance(response, requests.Response)
            self.assertEqual(response.status_code, 200)

    def test_request_with_multithreading_proxies_no_progress(self):
        # Define request options
        request_options = [
            {"url": "https://www.example.com"},
            {"url": "https://www.google.com"},
            {"url": "https://www.openai.com"},
        ]

        # Call the function
        responses = self.proxy_manager.request_with_multithreading_proxies(
            request_method=requests.get,
            request_options=request_options,
            countries=["NL", "FR"],
            number_of_threads=5,
            max_use_per_proxy=3,
            show_progress=False,
        )

        # Assertions
        self.assertEqual(len(responses), len(request_options))
        for response in responses:
            self.assertIsInstance(response, requests.Response)
            self.assertEqual(response.status_code, 200)

    def test_function_with_multithreading_proxies(self):
        # Divide the tracking number by chunks of 5 to avoid being blocked by UPS

        options = [
            {
                "tracking_numbers": ["1Z12345", "1Z12346", "1Z12347", "1Z12348"],
                "sensor_data": "info",
            }
        ]

        responses = self.proxy_manager.function_with_multithreading_proxies(
            request_method=self.get_delivery_info,
            request_options=options,
            countries=["US"],
            number_of_threads=1,
            max_use_per_proxy=1,
            show_progress=True,
        )
        for response in responses[0]:
            self.assertIsInstance(response, requests.Response)
            self.assertEqual(response.status_code, 200)

    def get_delivery_info(
        self, tracking_numbers: str, proxies: dict, sensor_data: str
    ) -> Tuple[List[requests.Response], List[str]]:
        responses = []
        for tracking_number in tracking_numbers:
            # Creating and persisting session
            with requests.Session() as session:
                for key, value in proxies.items():
                    if isinstance(value, str):  # Check if the value is a string
                        proxies[key] = value.replace("https", "http")

                    responses.append(
                        requests.request(
                            "GET",
                            "https://dummyjson.com/carts/",
                            headers={
                                "User-Agent": "Mozilla/5.0",
                                "TrackingNumber": tracking_number,
                                "SensorData": sensor_data,
                            },
                            proxies=proxies,
                        )
                    )
        return {
            "responses": responses,
            "tracking_numbers": tracking_numbers,
        }


if __name__ == "__main__":
    unittest.main()
