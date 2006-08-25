#!/bin/bash
#
# Run all tests
#

echo "Running UnitTests..."

python testcli.py
python testmenu.py
python testmedia.py
python testcairorender.py
python testeffect.py
python testflipbook.py
python testlayer.py

echo "Running interactive tests..."
python testcairodraws.py
