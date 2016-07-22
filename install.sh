#!/bin/sh
set -e
sudo apt-get install vim vim-snippets vim-tlib vim-youcompleteme cmake 
vim-addon-manager install tlib snippets youcompleteme
sudo mkdir /etc/cpprj
sudo cp lics/* /etc/cpprj/
sudo cp {CMakeLists.txt,Doxyfile,cli.cpp,lib.cpp} /etc/cpprj/
sudo chmod -R 644 /etc/cpprj/*
sudo cp cpprj /usr/bin
mkdir ~/projects
mkdir ~/.vim
cp vimrc ~/.vimrc
cp dummy_prj ~/projects/dummy
