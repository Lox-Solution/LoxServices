from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lox_services",
    version="0.3.1",
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
        "google-cloud == 0.34.0",
        "google-cloud-storage == 2.11.0",
        "google-cloud-bigquery == 3.12.0",
        "gspread == 5.11.3",
        "gspread-dataframe == 3.3.1",
        "pdfminer.six == 20221105",
        "weasyprint == 52.5",
        "requests == 2.31.0",
        "selenium == 4.12.0",
        "undetected-chromedriver == 3.1.3",
        "numpy == 1.26.0",
        "pandas == 2.1.1",
        "lxml == 4.9.3",
        "cryptography == 41.0.4",
        "paramiko == 3.3.1",
        "PyVirtualDisplay == 3.0",
        "mimesis == 11.1.0",
    ],
)
