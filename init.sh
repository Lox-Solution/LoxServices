#!/bin/bash

# To run with: sh init.sh
if [ -d "./venv" ]; then
    echo "The Virtual Environment 'venv' has already been created, skipping creation."
    return 0
fi

echo "Creating Virtual Environment as 'venv'..."
virtualenv -p /usr/bin/python3.8 venv # if this command doesn't work, make sure to install virtualenv on your machine
