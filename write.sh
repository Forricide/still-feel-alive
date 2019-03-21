#!/bin/bash

git add . && git commit -m "$1" && git push
./update-site.sh "$1"
rm *.md.gi.html
