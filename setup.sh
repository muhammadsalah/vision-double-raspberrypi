#!/bin/sh

sudo apt-get update
#sudo apt-get upgrade
#sudo rpi-update

# install needed python libraries
sudo apt-get -y install libopencv-dev python-opencv 
sudo apt-get -y install python-picamera 

# enable opengl on rpi
sudo apt-get -y install libgl1-mesa-dri

# IoT packages 
sudo apt-get -y install python-setuptools python-dev build-essential 
sudo easy_install pip 
sudo pip install ibmiotf


echo "Done, but reboot is required."

