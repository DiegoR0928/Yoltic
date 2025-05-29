#!/bin/bash

# Cámara 1
gst-launch-1.0 -v \
v4l2src device=/dev/video2 ! \
video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! \
videoconvert ! \
x264enc tune=zerolatency bitrate=3000 speed-preset=superfast key-int-max=30 ! \
mpegtsmux ! \
udpsink host=192.168.1.75 port=9000 sync=false async=false &

# Cámara 2
gst-launch-1.0 -v \
v4l2src device=/dev/video5 ! \
video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! \
videoconvert ! \
x264enc tune=zerolatency bitrate=3000 speed-preset=superfast key-int-max=30 ! \
mpegtsmux ! \
udpsink host=192.168.1.75 port=9001 sync=false async=false &

# Cámara 3
gst-launch-1.0 -v \
v4l2src device=/dev/video8 ! \
video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! \
videoconvert ! \
x264enc tune=zerolatency bitrate=3000 speed-preset=superfast key-int-max=30 ! \
mpegtsmux ! \
udpsink host=192.168.1.75 port=9002 sync=false async=false &

# Espera a que ambos procesos terminen
wait