#!/bin/bash

python3 compile.py *.md
git add . && git commit -m "$1" && git push
rm *.md.gi.html
