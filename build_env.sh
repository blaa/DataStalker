#!/bin/bash

if [ -f "ENV" ]; then
    echo "Virtualenv exists already - to refresh delete it manually"
    sleep 2
else
    python3 -m venv ENV
fi

. ./ENV/bin/activate

echo "Installing required packages"
pip3 install wheel
pip3 install -r requirements.txt

echo "Activate venv with '. ./ENV/bin/activate'"
