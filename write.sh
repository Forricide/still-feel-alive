#!/bin/bash

python compile.py
git add . && git commit -m "$1" && git push
rm *.md.html
