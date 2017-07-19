Installation
============

- On the Raspberry Pi, run ```./setup.sh```
- On a Mac, make sure [homebrew][] is installed, then run ```./setup_macos.sh```
- Create a config file: ```cp config.yml.sample config.yml```
- Edit the config file:
  - Set ```rpi_camera``` to ```True``` if using the official Raspberry Pi camera, else ```False``` for a USB webcam
  - Set ```camera_number``` to ```0``` for first webcam (or iSight cam on Mac)

Running
=======

- Run ```./run.sh```

  [homebrew]: http://brew.sh/