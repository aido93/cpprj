#!/bin/sh
set -e
#sudo apt-get install vim vim-snippets vim-tlib vim-youcompleteme cmake 
#vim-addon-manager install tlib snippets youcompleteme
sudo mkdir /etc/cpprj
sudo cp lics/* /etc/cpprj/
sudo cp CMakeLists.txt /etc/cpprj/
sudo cp Doxyfile /etc/cpprj/
sudo cp cls_dummy* /etc/cpprj/
sudo cp cli.cpp /etc/cpprj/
sudo chmod -R 644 /etc/cpprj/*
sudo cp cpprj /usr/bin
sudo cp cclass /usr/bin
sudo cp rmclass /usr/bin
mkdir ~/projects
cp dummy_prj ~/projects/dummy
