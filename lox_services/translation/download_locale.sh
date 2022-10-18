#!/bin/sh

# Set color to yellow
echo '\033[0;33m' 

# Params:
language=$1
encoding=$2

if [ -z "$language" ]; then
    echo "Error: missing arguments."
    echo "Usage: $0 language [encoding]"
    echo '\e[0m' # reset color
    exit 1
fi

if [ -z "$encoding" ]; then
    encoding="utf8"
fi

if (locale -a | grep $language.$encoding); then
    echo "Locale '$language.$encoding' already installed."

else 
    echo "Locale $language.$encoding not installed."
    echo "Installing..."
    sudo locale-gen $language.$encoding
    echo "Locale $language.$encoding installed."
fi

echo '\e[0m' # reset color
exit 0