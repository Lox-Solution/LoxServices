import unittest
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


if __name__ == "__main__":
    unittest.main()
