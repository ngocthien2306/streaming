import cv2
import time 

from utils import model
from utils.logging_system import logger
from utils.project_config import project_config
from utils.utils import *
import requests

if project_config.STREAM_ENGINE == "VLC":
    from streaming.vlc_streaming import VLCStreaming as StreamEngine
elif project_config.STREAM_ENGINE == "GS":
    from streaming.gs_streaming import GSStreaming as StreamEngine



class StreamManage:
    def __init__(self) -> None:
        self._players = {}
        self._cameras = {}

        self._ouput_players = {}
        self._cameras_id = []
        self._cameras_rtsp_link = []

        self._prefix_topic = "streaming_"
    
        self.init()
    
    def get_camera_by_server_name(self):
        server_name = get_computer_name()
        root_url = f'http://172.20.10.2:8080/camera/{server_name}'
        res = requests.get(root_url)
        content = res.json()
        return content['data']['cameras']
    
    def update_ip(self):
        root_url = f'http://172.20.10.2:8080/server/update-ip'
        res = requests.put(root_url, json={'ip': get_ipv4_address(), 'server_name': get_computer_name()})
        content = res.json()
        print(content)
        


    def init(self):
        self.update_ip()        
        all_records = self.get_camera_by_server_name()
        
        for record in all_records:
            record.pop("id")
            camera = model.Camera(**record)
            self._cameras_id.append(camera.camera_id)
            self._cameras_rtsp_link.append(camera.rtsp_link)
            self._cameras[camera.camera_id] = camera
            self._players[camera.camera_id] = StreamEngine(
                    rtsp_link=camera.rtsp_link,
                    producer=None,
                    frame_rate=camera.frame_rate,
                    output_size=(camera.output_width, camera.output_height),
                    camera_id=camera.camera_id
                    )
            logger.info(f"Init Camera: {camera.dict()}")

    def add_camera(self, camera: model.Camera):

        logger.info(f"Add Camera: {camera.dict()}")
        self._cameras_id.append(camera.camera_id)
        self._cameras_rtsp_link.append(camera.rtsp_link)

        self._cameras[camera.camera_id] = camera
        self._players[camera.camera_id] = StreamEngine(
                    rtsp_link=camera.rtsp_link,
                    producer=None,
                    frame_rate=camera.frame_rate,
                    output_size=(camera.output_width, camera.output_height)
                    )

        
        return model.CameraResponse(
            **{
                **camera.dict(), 
                "state": self._players[camera.camera_id].get_state()
            })

    def delete_camera(self, camera_id: str):

        logger.info(f"Delete Camera: {camera_id}")
        camera = self._cameras.get(camera_id)
        self._cameras_id.remove(camera_id)
        self._cameras_rtsp_link.remove(camera.rtsp_link)
        self._players[camera_id].stop_stream()
        
        del self._cameras[camera_id]
        del self._players[camera_id]
        
        return ""


    def get_camera(self, camera_id: str):
        camera = self._cameras.get(camera_id)
        return model.CameraResponse(**{
                **camera.dict(), 
                "state": self._players[camera.camera_id].get_state()
            })

    def get_all_cameras(self):
        for camera_id in self._cameras_id:
            yield self.get_camera(camera_id)

    def check_camera_id_exist(self, camera_id: str):
        return camera_id in self._cameras_id

    def check_rtsp_exist(self, rtsp_link: str):
        return rtsp_link in self._cameras_rtsp_link

    def get_player_by_id(self, camera_id: str) -> StreamEngine:
        return self._players.get(camera_id)

    def post_output(self, frame_bytes, module_id):
        self._ouput_players[module_id] = frame_bytes
    
    def get_output(self, module_id):
        """A generator for the image."""
        header = "--jpgboundary\r\nContent-Type: image/jpeg\r\n"
        prefix = ""
        while True:
            frame = self._ouput_players.get(module_id, b"")
            msg = (
                prefix
                + header
                + "Content-Length: {}\r\n\r\n".format(len(frame))
            )

            yield (msg.encode("utf-8") + frame)
            prefix = "\r\n"
            time.sleep(0.05)