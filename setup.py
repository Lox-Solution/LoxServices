from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lox_services",
    version="0.1.29",
    author="Lox Solution",
    author_email="natasa.zekic@loxsolution.com",
    description="A package with Lox services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lox-Solution/LoxServices",
    project_urls={"Bug Tracker": "https://github.com/Lox-Solution/LoxServices/issues"},
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "google-cloud >= 0.34.0",
        "google-cloud-storage >= 1.38.0",
        "google-cloud-bigquery >= 2.10.0",
        "gspread >= 4.0.1",
        "gspread-dataframe >= 3.2.1",
        "slack_sdk >= 3.0.0, < 4.0.0",
        "pdfminer >= 20191125",
        "weasyprint == 52.5",
        "requests >= 2.23.0",
        "selenium >= 4.0.0",
        "undetected-chromedriver >= 3.0.3",
        "selenium-wire >= 4.5.4",
        "xvfbwrapper >= 0.2.9",
        "numpy >= 1.22.4",
        "pandas >= 1.4.2",
        "tabula-py == 2.2.0",
        "pytz >= 2021.1",
        "lxml >= 4.9.1",
        "cryptography >= 37.0.2",
        "paramiko >= 2.11.0",
        "PyVirtualDisplay >= 3.0",
        "mimesis >= 7.0.0",
    ],
)
