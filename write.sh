#!/bin/bash

python compile.py *.md
git add . && git commit -m "$1" && git push
rm *.md.html
