#! /bin/bash

python3.9 -m venv temp
. temp/bin/activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller -w -F run_client.py
cp -r assets dist
deactivate
rm -rf temp