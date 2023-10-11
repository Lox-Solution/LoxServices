#!/bin/bash

# To run with: sh init.sh

if [ -d "./venv" ]; then
    echo "The Virtual Environment 'venv' has already been created, skipping creation."
    exit 0
fi

echo "Creating Virtual Environment as 'venv'..."

# A list of potential paths for Python3
python_paths=("/usr/bin/python3" "/usr/local/bin/python3" "/opt/homebrew/bin/python3")

python_path=""

# Find the Python 3.11 path that exists
for path in "${python_paths[@]}"; do
    if [ -x "$path" ]; then
        version_string="$($path --version 2>&1)"
        if [[ $version_string == *"Python 3.11"* ]]; then
            python_path="$path"
            break
        fi
    fi
done

# Check if a valid Python path was found
if [ -z "$python_path" ]; then
    echo "Python3 not found in the predefined paths. Please install Python3 or check your installation."
    exit 1
fi

virtualenv -p "$python_path" lox-env # if this command doesn't work, make sure to install virtualenv on your machine
