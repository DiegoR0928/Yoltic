#!/bin/bash

# Cámara 1
gst-launch-1.0 -v \
v4l2src device=/dev/video4 ! \
video/x-raw,format=YUY2,width=1280,height=720,framerate=30/1 ! \
videoconvert ! \
x264enc tune=zerolatency bitrate=3000 speed-preset=superfast key-int-max=30 ! \
mpegtsmux ! \
udpsink host=192.168.1.101 port=9000 sync=false async=false

# Espera a que terminen
wait
