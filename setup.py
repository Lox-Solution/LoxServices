import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='lox_services',
    version='0.0.1',
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
    packages=['lox_services', 'lox_services/email', 'lox_services/translation'],
)
