# LoxServices
This README was exported from [this Notion page](https://www.notion.so/loxsolution/Python-private-packages-eeb51ca4b8bd471991c9d7ea01d68b50) the 19th of July 2022.
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

Every time you call `pip install git+https://github.com/Lox-Solution/LoxServices.git`, pip checks the version number in the `setup.py` file, and if needed, the package gets updated. If you add the flag *—update*, pip will uninstall and then reinstall the latest version.

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
    

## Contribution instructions

To add your code to the package please follow the next steps:

1. Make a new branch as usual and add your code (lox_services folder)
2. Write some tests for your code (tests folder)
3. Make sure there is an `__init__.py` file in the folder you added code to, otherwise the package won’t be able to see your code.
4. In case you are adding non-code (data) files (e.g., *.json, .csv, .pdf)*, make sure to include them in document `MANIFEST.in` .
5. Push your commit to GitHub but don’t make PR yet.
6. Run the command below in your terminal and test your addition via package (change **branch-name** in command to fit your branch)
    
    ```bash
    #Install package with all the latest changes from a branch
    pip install git+https://github.com/Lox-Solution/LoxServices.git@**branch-name** --upgrade
    ```
    
7. If everything works fine, record additions to the `CHANGELOG.md` and increment the version in the setup file.
8. Request PR and check the status of the tests. The tests run automatically on PR creation so in case they fail fix the issues otherwise you won’t be able to merge changes.
