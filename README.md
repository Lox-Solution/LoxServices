# LoxServices
This README was exported from [this Notion page](https://www.notion.so/loxsolution/Python-private-packages-eeb51ca4b8bd471991c9d7ea01d68b50) the 30th of August 2022.
## GitHub SSH access

If you are developing, make sure to connect via SSH. To do so, follow the [GitHub tutorial](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) and it should be fine. Make sure to add your computer’s key in your own GitHub settings.

If you are working on a VM, or the cloud, follow this [GitHub tutorial](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) to generate an SSH key. Here is a little helper for ssh key generation: 

```bash
cd Main-Algorithms # Go to the root of the project
ssh-keygen -t ed25519 -C "name-your-key" -q -N ""
# cf [ssh-keygen documentation](https://man.openbsd.org/cgi-bin/man.cgi/OpenBSD-current/man1/ssh-keygen.1?query=ssh-keygen&sec=1) for more details
# The path will be printed, remember the deploy key's name.
```

After generating your key you send the **PUBLIC** (not private!) part of the key to @Nataša Zekić or @Alexandre Girbal so they can add your key to the repository. Then you can try to install the package. If you have an error, maybe there is more than one ssh key on your computer. In that case, you need to add a piece of configuration to continue.

Go in the computer’s SSH configuration file (usually `~/.ssh/config`), and add an alias entry for each repository. For example:

```
Host github.com/LoxSolution
        Hostname github.com
        IdentityFile=/absolut_path/.ssh/deploy_key
```

## Install / Update package

To install the lox_services package, run the command below in your activated virtual environment:

```bash
#Install the latest version from the master branch
pip install git+ssh://git@github.com/Lox-Solution/LoxServices.git
#Install the version of your choice from the master branch (e.g., version 0.0.5)
pip install git+ssh://git@github.com/Lox-Solution/LoxServices.git@**v0.0.5**
#Install a version from a branch of your choice (e.g., develop)
pip install git+ssh://git@github.com/Lox-Solution/LoxServices.git@**branch-name**
#Install a version from a commit of your choice
pip install git+ssh://git@github.com/Lox-Solution/LoxServices.git@**commit-hash**
```

Every time you call `pip install git+ssh://git@github.com/Lox-Solution/LoxServices.git`, pip checks the version number in the `setup.py` file, and if needed, the package gets updated. If you add the flag *—upgrade*, pip will uninstall and then reinstall the latest version.

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

1. Make a new branch as usual and add your code (lox_services folder with respect to the rules stated above)
2. Write some tests for your code (tests folder)
3. Make sure there is an `__init__.py` file in the folder you added code to, otherwise the package won’t be able to see your code.
4. In case you are adding non-code (data) files (e.g., *.json, .csv, .pdf)*, make sure to include them in document `MANIFEST.in` .
5. Push your commit to GitHub but don’t make PR yet.
6. Run the command below in your terminal and test your addition via package (change **branch-name** in command to fit your branch).
    
    ```bash
    #Install package with all the latest changes from a branch
    pip install git+ssh://git@github.com/Lox-Solution/LoxServices.git@**branch-name** --upgrade
    ```
    
7. If everything works fine, record additions to the `CHANGELOG.md` and increment the version in the setup file. 
8. In case your code depends on some other packages, check if they are already defined in the `setup.py` file in `install_requires` line and if necessary add them.
9. Request PR and check the status of the tests. The tests run automatically on PR creation so in case they fail fix the issues otherwise you won’t be able to merge changes.
