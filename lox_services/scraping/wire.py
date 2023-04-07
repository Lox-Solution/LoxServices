import json
from seleniumwire.undetected_chromedriver.v2 import Chrome
from seleniumwire.utils import decode
from pprint import pprint

driver = Chrome()
with driver:
    tracking_number = "792690"
    driver.get(
        f"https://www.dhl.com/nl-en/home/tracking/tracking-ecommerce.html?submit=1&tracking-id={tracking_number}"
    )
    utapi_request = driver.wait_for_request(
        "www.dhl.com/utapi", 5
    )  # Waits for bot Checking max 5 sec
    print(utapi_request.url)
    utapi_response = utapi_request.response
    utapi_body = decode(
        utapi_response.body, utapi_response.headers.get("Content-Encoding", "identity")
    )
    body = json.loads(utapi_body)
    # print(body)
    pprint(body["shipments"])
