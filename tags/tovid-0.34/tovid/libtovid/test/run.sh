#!/bin/bash
#
# Run all tests
#

echo "Running UnitTests..."

python test_cli.py
python test_menu.py
python test_media.py
python test_cairo_funcs.py
python test_cairo_newfuncs.py
python test_effect.py
python test_flipbook.py
python test_layer.py

echo "Running interactive tests..."
python test_cairo_drawings.py
