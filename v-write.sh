#!/bin/bash

git add . && git commit -m "$1" && git push && git push gh master
./v-update-site.sh "$1"
