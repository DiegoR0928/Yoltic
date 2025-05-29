# video/pipelines.py
from .live_pipeline import LivePipeline

live_pipelines = {}
pipelines_initialized = False

def init_pipelines():
    global pipelines_initialized, live_pipelines
    if not pipelines_initialized:
        print("Inicializando pipelines...")

        live_pipelines = {
            1: LivePipeline("rtsp://192.168.1.75:8554/cam1", 5000),
            2: LivePipeline("rtsp://192.168.1.75:8554/cam2", 5001),
            3: LivePipeline("rtsp://192.168.1.75:8554/cam3", 5002),
        }

        try:
            for pipeline in live_pipelines.values():
                pipeline.start()
            pipelines_initialized = True
        except Exception as e:
            print("Error iniciando pipelines:", e)
