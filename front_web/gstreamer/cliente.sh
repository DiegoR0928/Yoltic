gst-launch-1.0 -v \
  rtspsrc location=rtsp://192.168.1.79:8554/cam1 latency=100 ! \
  decodebin ! videoconvert ! jpegenc ! \
  udpsink host=127.0.0.1 port=5000
