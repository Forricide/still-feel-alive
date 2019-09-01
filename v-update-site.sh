#!/bin/bash

python3 compile.py *.md -v
cd ~/writing/forwebsite/
git add .
git commit -m "$1" && git push
