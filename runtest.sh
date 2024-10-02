#!/bin/bash

coverage erase
cd ./tests/
find . -iname '*_tests.py' -type f -exec coverage3 run -a {} \;
coverage report -m
coverage html
read tmp