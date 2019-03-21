#!/bin/bash

git add . && git commit -m "$1" && git push && git push gh master
./update-site.sh "$1"
