#!/bin/bash

# To run with: source activate.sh
source venv/bin/activate

pip install -r requirements.txt # > /dev/null

export PYTHONPATH=$(pwd)/src