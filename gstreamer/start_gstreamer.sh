#!/bin/bash

# IP destino (donde está MediaMTX o el receptor)
DEST_IP="192.168.1.100"

# Puertos para RTP y RTCP (uno para cada cámara)
RTP_PORT1=5000
RTCP_PORT1=5001

RTP_PORT2=5002
RTCP_PORT2=5003

RTP_PORT3=5004
RTCP_PORT3=5005

# Cámara 1
gst-launch-1.0 -v \
realsense2src serial=CAMERA1_SERIAL ! \
videoconvert ! video/x-raw,framerate=30/1 ! \
x264enc tune=zerolatency ! \
rtph264pay pt=96 config-interval=1 ! \
rtpbin name=rtpbin \
rtpbin.send_rtp_sink_0 ! udpsink host=$DEST_IP port=$RTP_PORT1 bind-port=40000 \
rtpbin.send_rtcp_src_0 ! udpsink host=$DEST_IP port=$RTCP_PORT1 sync=false async=false \
udpsrc port=40001 ! rtpbin.recv_rtcp_sink_0 &

# Cámara 2
gst-launch-1.0 -v \
realsense2src serial=CAMERA2_SERIAL ! \
videoconvert ! video/x-raw,framerate=30/1 ! \
x264enc tune=zerolatency ! \
rtph264pay pt=96 config-interval=1 ! \
rtpbin name=rtpbin \
rtpbin.send_rtp_sink_0 ! udpsink host=$DEST_IP port=$RTP_PORT2 bind-port=40002 \
rtpbin.send_rtcp_src_0 ! udpsink host=$DEST_IP port=$RTCP_PORT2 sync=false async=false \
udpsrc port=40003 ! rtpbin.recv_rtcp_sink_0 &

# Cámara 3
gst-launch-1.0 -v \
realsense2src serial=CAMERA3_SERIAL ! \
videoconvert ! video/x-raw,framerate=30/1 ! \
x264enc tune=zerolatency ! \
rtph264pay pt=96 config-interval=1 ! \
rtpbin name=rtpbin \
rtpbin.send_rtp_sink_0 ! udpsink host=$DEST_IP port=$RTP_PORT3 bind-port=40004 \
rtpbin.send_rtcp_src_0 ! udpsink host=$DEST_IP port=$RTCP_PORT3 sync=false async=false \
udpsrc port=40005 ! rtpbin.recv_rtcp_sink_0 &

# Espera a que terminen
wait