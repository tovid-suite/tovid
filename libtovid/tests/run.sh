#!/bin/bash
#
# Run all tests
#

echo "Running UnitTests..."

python testcli.py
python testmenu.py
python testmedia.py
python testcairorender.py

