gst-launch-1.0 -v \
  rtspsrc location=rtsp://192.168.1.101:8554/cam1 latency=0 ! \
  decodebin ! videoconvert ! jpegenc quality=50 ! \
  multipartmux boundary=frame ! \
  tcpserversink host=127.0.0.1 port=5000 sync=false
