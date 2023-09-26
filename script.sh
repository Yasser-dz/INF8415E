#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root using sudo .\script.sh"
  exit
fi
rm -rf LOG8415E
git clone https://github.com/Yasser-dz/INF8415E.git
#cd LOG8415E/tp1
chmod +x run.sh
./run.sh