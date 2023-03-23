#!/bin/bash

# To run with: source activate.sh
source venv/bin/activate

pip install -r requirements.txt # > /dev/null

export ENVIRONMENT='development'
echo -e "--- using DEVELOLPMENT environment${NC}\n"

export PYTHONPATH=$(pwd)
echo -e "--- PYTHONPATH: ${NC} $PYTHONPATH ---"
