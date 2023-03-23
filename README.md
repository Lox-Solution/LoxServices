# LoxServices
This README was exported from [this Notion page](https://www.notion.so/loxsolution/Python-private-packages-eeb51ca4b8bd471991c9d7ea01d68b50) the 19th of December 2022.
## Disclaimer

The first and most important thing to know is that the LoxServices repository is **PUBLIC**. It means that you have to be extremely careful with the information you put in the code. Do not hardcode any tokens, emails, Lox, or client information.

## Install / Update package

To install the lox_services package, run the command below in your activated virtual environment:

```bash
#Install the latest version from the master branch
pip install git+https://github.com/Lox-Solution/LoxServices.git
#Install the version of your choice from the master branch (e.g., version 0.0.5)
pip install git+https://github.com/Lox-Solution/LoxServices.git@**v0.0.5**
#Install a version from a branch of your choice (e.g., develop)
pip install git+https://github.com/Lox-Solution/LoxServices.git@**branch-name**
#Install a version from a commit of your choice
pip install git+https://github.com/Lox-Solution/LoxServices.git@**commit-hash**
```

Every time you call `pip install git+https://github.com/Lox-Solution/LoxServices.git`, pip checks the version number in the `setup.py` file, and if needed, the package gets updated. If you add the flag *—upgrade*, pip will uninstall and then reinstall the latest version.

## Package structure

The package is hosted in the [LoxServices repository](https://github.com/Lox-Solution/LoxServices) with the following structure:

```markup
**LoxServices**
├── CHANGELOG.md               ┐
├── LICENSE                    │ Package documentation
├── README.md                  ┘
├── setup.py                   ┐
├── MANIFEST.in                │
├── lox_services               │ Package source code, metadata,
│   └── email                  │ and build instructions
│   └── translation            │
│   ...                        │
│   └── __init__.py            ┘
└── tests                      ┐
    └── ...                    ┘ Package tests
```

- Package documentation

    File `CHANGELOG.md` is basically a version tracker and contains records of all the additions to the package.

    `LICENSE.md` and `README.md` files are self-explanatory.

- Package build instructions

    File `setup.py` is a configuration file and contains installation instructions.

    File `MANIFEST.in` contains a list of non-code files to include in the package.

- Package tests

    Package tests make sure the code works as it’s supposed to. Tests run on PR on develop and push to master. Every function in the package **must** have its own test in case of failure and success.


## Contributions to lox_services

### Rules

Service is a module that contains a set of generic functionalities related to one particular subject, e.g. email. Here are a few rules about services:

- services names are **singular,**
- services names are **lowercased,**
- services serve **one and only one subject**, e.g. *scraping* and *fetching*, not *scraping_and_fetching,*
- services **can** be composed of **multiple sub-services**, e.g. *persistence* → *storage*, *database*, …

### Step-by-step instructions

To add your code to the lox_services package please follow the next steps:

1. **Step**: make a new branch as usual and add your code (lox_services folder with respect to the rules stated above)
2. **Step**: write some tests for your code (tests folder)
3. **Step**: make sure there is an `__init__.py` file in the folder you added code to, otherwise the package won’t be able to see your code.
4. **Step**: in case you are adding non-code (data) files (e.g., *.json, .csv, .pdf)*, make sure to include them in document `MANIFEST.in` .
5. **Step**: make sure you didn’t hardcode any information that shouldn’t be public!!!
6. **Step**: push your commit to GitHub but don’t make PR yet.
7. **Step**: run the command below in your terminal and test your addition via package (change **branch-name** in command to fit your branch).

    ```bash
    #Install package with all the latest changes from a branch
    pip install git+https://github.com/Lox-Solution/LoxServices.git@**branch-name** --upgrade
    ```

8. **Step**: if everything works fine, record additions to the `CHANGELOG.md` and increment the version in the setup file.
9. **Step**: in case your code depends on some other packages, check if they are already defined in the `setup.py` file in `install_requires` line and if necessary add them.
10. **Step**: request PR and check the status of the tests. The tests run automatically on PR creation so in case they fail fix the issues otherwise you won’t be able to merge changes.

---

## Additional reading (optional)

- [https://towardsdatascience.com/create-your-custom-python-package-that-you-can-pip-install-from-your-git-repository-f90465867893](https://towardsdatascience.com/create-your-custom-python-package-that-you-can-pip-install-from-your-git-repository-f90465867893)
- [https://docs.readthedocs.io/en/stable/guides/private-python-packages.html](https://docs.readthedocs.io/en/stable/guides/private-python-packages.html)
- [https://docs.github.com/en/developers/overview/managing-deploy-keys#deploy-keys](https://docs.github.com/en/developers/overview/managing-deploy-keys#deploy-keys)
