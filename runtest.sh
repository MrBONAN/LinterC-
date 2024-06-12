#!/bin/bash

coverage3 erase
find . -iname '*_tests.py' -type f -exec coverage3 run -a {} \;
coverage3 report -m