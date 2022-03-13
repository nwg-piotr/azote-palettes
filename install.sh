#!/usr/bin/env bash

python3 setup.py install --optimize=1
cp azote-palettes.svg /usr/share/pixmaps/
cp azote-palettes.desktop /usr/share/applications/