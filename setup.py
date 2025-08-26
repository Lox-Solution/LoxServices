from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lox_services",
    version="1.2.44",
    author="Lox Solution",
    author_email="melvil.donnart@loxsolution.com",
    description="A package with Lox services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lox-Solution/LoxServices",
    project_urls={"Bug Tracker": "https://github.com/Lox-Solution/LoxServices/issues"},
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7, <=3.12",
    install_requires=[
        "google-cloud",
        "google-cloud-storage",
        "google-cloud-bigquery",
        "gspread",
        "gspread-dataframe",
        "pdfminer.six",
        "weasyprint",
        "requests",
        "selenium",
        "undetected-chromedriver",
        "selenium-wire",
        "xvfbwrapper",
        "numpy",
        "pandas",
        "lxml",
        "cryptography",
        "tabula-py",
        "paramiko",
        "PyVirtualDisplay",
        "mimesis",
    ],
)
