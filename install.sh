#!/usr/bin/env bash

python3 setup.py install --optimize=1
cp dist/azote-palettes.svg /usr/share/pixmaps/
cp dist/azote-palettes.desktop /usr/share/applications/