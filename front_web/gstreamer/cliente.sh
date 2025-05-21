gst-launch-1.0 -v \
rtspsrc location=rtsp://192.168.1.74:8554/cam1 latency=300 ! \
decodebin ! videoconvert ! \
queue ! videorate ! video/x-raw,framerate=10/1 ! videoscale ! video/x-raw,width=320,height=240 ! \
jpegenc quality=80 ! \
udpsink host=127.0.0.1 port=5000 sync=false async=false &

gst-launch-1.0 -v \
rtspsrc location=rtsp://192.168.1.74:8554/cam2 latency=200 ! \
decodebin ! videoconvert ! \
queue ! videorate ! video/x-raw,framerate=10/1 ! videoscale ! video/x-raw,width=320,height=240 ! \
jpegenc quality=80 ! \
udpsink host=127.0.0.1 port=5001 sync=false async=false &

gst-launch-1.0 -v \
rtspsrc location=rtsp://192.168.1.74:8554/cam3 latency=300 ! \
decodebin ! videoconvert ! \
queue ! videorate ! video/x-raw,framerate=10/1 ! videoscale ! video/x-raw,width=320,height=240 ! \
jpegenc quality=80 ! \
udpsink host=127.0.0.1 port=5002 sync=false async=false &

wait
