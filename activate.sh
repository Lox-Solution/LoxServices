#!/bin/bash

# To run with: source activate.sh
source lox-env/bin/activate

pip install -r requirements.txt # > /dev/null

export ENVIRONMENT='development'
echo -e "--- using DEVELOPMENT environment${NC}\n"

export PYTHONPATH=$(pwd)
echo -e "--- PYTHONPATH: ${NC} $PYTHONPATH ---"
