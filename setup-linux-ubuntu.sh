#!/bin/bash

export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"

sudo apt install -y python3 python3-pip
sudo -H pip3 install lxml networkx numpy scipy gitpython openpyxl

if [ ! -f misc/.done ]; then
  cd misc/
  sudo ./apply_patch.py
  touch .done
  cd ..
fi

if [ ! -d ./repos/linux ]; then
  git clone https://github.com/torvalds/linux.git ./repos/linux
  git -C ./repos/linux checkout v4.10
fi

if [ ! -f srcML-Ubuntu14.04-64.deb ]; then
  wget http://131.123.42.38/lmcrs/beta/srcML-Ubuntu14.04-64.deb
  sudo dpkg -i srcML-Ubuntu14.04-64.deb
  sudo apt install -y libarchive-dev libcurl3 
fi

if [ ! -d ./repos/linux-4.10-xml/ ]; then
  ./graphs/srcml.py ./repos/linux ./repos/linux-4.10-xml/
fi

