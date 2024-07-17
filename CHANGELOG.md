0.0.1 initial package with email service
0.0.2 translation service added
0.0.3 support translation functions added
0.0.4 data files added
0.0.5 tests for translation service added
0.0.6 fix MANIFEST.in content
0.0.7 configuration path and env variables added
0.0.8 utils functions added
0.0.9 email, encryption, finance, pdf, persistence, proxy, scraping and slack service added
0.1.0 carrier service: Chronopost, Colissimo, Colisprive available with selenium xvfb
0.1.1 Add translations for billing
0.1.2 Update translation key order number
0.1.3 Fix assets in billing service
0.1.4 Add local language download feature
0.1.5 Remove finance service and update all services
0.1.6 Add Postmark function in email.static sub-service
0.1.7 Cleaned and updated all the files (ready for launch)
0.1.8 Add protocol service
0.1.9 Add VirtualDisplay decorator
0.1.10 Add Chrome options for cloud usage with selenium
0.1.11 Use CLOUD_ROOT_PATH instead of ROOT_PATH
0.1.12 Fix circular dependency
0.1.13 Added a fake name generator
0.1.14 Added parameterized query, screenshoting in selenium exceptions, uploading of output folder to GCS
0.1.15 Added tagging members in slack, switched to dotenv package for env variables
0.1.16 Added temporary table function, cache proxy IPs per country, load_table_from_dataframe function, metadata columns, integrate black formatting
0.1.17 Added regex utility function, postal code processing, country validation and adapted lox bills statements
0.1.18 Fixed screenshot crash feature
0.1.19 Fixed missing codes from pycountry package, added function to save to pdf from base 64
0.1.20 Added function to find local chrome version, function to handle multiple brightdata requests and currency conversion table check
0.1.21 Improved chromedriver service
0.1.22 Added unit testing and implemented code coverage, added retry decorator
0.1.23 Added badge to readme and missing translation for invoice generation, removed check on invoice_url value
0.1.24 Added selenium wire chromedriver, fixed client invoices data quality check
0.1.25 Added unit test on email and chromedriver, new selenium_utils function, turned of coverage patch
0.1.26 Added quality check on deliveries, decorator for production functions only and google storage file removal
0.1.27 Hotfix on remove_duplicate_deliveries function
0.1.28 Hotfix on selenium wire
0.1.29 Hotfix on selenium wire
0.2.0 Added timestamp removal, bulk blob removal form storage, base64 to dataframe transformation and updated reason refunds
0.3.0 Added package information validation function
0.3.1 Removed chromedriver tests, update datasets enums
1.0.0 Transition from Python 3.8 to 3.11
1.0.1 Hotfix on chromedriver incognito mode
1.0.2 Hotfix on python versions required
1.0.3 Align the requirements and the setup packages
1.0.4 Hotfix resizing chromedriver
1.0.5 Hotfix allowing Colissimo specific translation
1.0.6 Hotfix allowing seleniumwire to run
1.1.0 Remove country code validation
1.2.0 Add RecordedActivity dataset
1.2.1 Optimize Query to remove duplicates on package information, add default original currency columns
1.2.2 fix package information remove duplicates
1.2.3 Make sure virtual display wraps all functions
1.2.4 Include all reason refunds in check duplicates
1.2.5 Add new table (pdf) into dataset
1.2.6 Fix download folder chromedriver
1.2.7 New functions on Brightdata
1.2.8 Add UploadedFiles in dataset
1.2.9 Add possibility to have cid images inside emails
1.2.10 Add the possibility to query table functions from SQL
1.2.11 Add UserActions in dataset
1.2.12 Allow the use of proxy on chromedriver
1.2.13 Allow Reply-To on emails sent
1.2.14 Read account_number as str
1.2.15 Add new table