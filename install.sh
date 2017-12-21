#!/bin/bash

set -e

mkdir -p        /etc/cpprj
cp -a lic       /etc/cpprj/
cp structs.py   /etc/cpprj/
cp enums.py     /etc/cpprj/
cp functions.py /etc/cpprj/
cp decor.py     /etc/cpprj/
cp class_gen.py /etc/cpprj/
cp Doxyfile     /etc/cpprj/

mkdir -p ~/projects
cp test_project.json ~/projects/
cp test_project.py   ~/projects/

cp cpprj.py /usr/bin/

