from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='lox_services',
    version='0.0.9',
    author='Lox Solution',
    author_email='natasa.zekic@loxsolution.com',
    description='A package with Lox services',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Lox-Solution/LoxServices',
    project_urls = {
        "Bug Tracker": "https://github.com/Lox-Solution/LoxServices/issues"
    },
    license='MIT',
    packages=find_packages(),
    include_package_data = True,
)
