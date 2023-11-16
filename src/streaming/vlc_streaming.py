import time
import threading
import ctypes
import cv2
import vlc
import numpy as np
from PIL import Image

from utils.project_config import stream_config
from utils.constants import CameraState
from utils.logging_system import logger
import requests

class VLCStreaming:
    last_frame = None
    last_ready = None
    lock = threading.Lock()
    vlc_instance = vlc.Instance(f'--no-audio --network-caching={stream_config.NETWORK_CACHING}')

    def __init__(self, rtsp_link, producer, frame_rate=6, output_size=(1280, 720), camera_id=None):
        self.rtsp_link = rtsp_link
        self.frame_rate = frame_rate
        self.stop = threading.Event()
        self.last_frame = None
        self.image_arr = None
        self.image_bytes = None
        self.new_image = False
        self.width_frame, self.height_frame = output_size

        self._camera_id = camera_id
        self._state = CameraState.INIT
        self._is_running_decode = True
        self._is_running_play_stream = True
        self._producer = producer


        self._play_thread = threading.Thread(target=self._play_stream_process)
        self._play_thread.daemon = True
        self._play_thread.start()

        self._decode_thread = threading.Thread(target=self._decode_frame_process)
        self._decode_thread.daemon = True
        self._decode_thread.start()

        logger.info(f"VLC Init Streaming: {self.rtsp_link}")
        
    def update_camera_status(self):
        try:
            root_url = f'http://172.20.10.2:8080/camera/update-status'
            res = requests.put(root_url, json={'camera_id': self._camera_id, 'camera_status': self._state})
            content = res.json()
            print(content)
        except Exception as e:
            logger.error(f"Call API ocour an error: {str(e)}")
            

    def _decode_frame_process(self):
        while self._is_running_decode:
            try:
                self.stop.clear()
                self.stop.wait()
                imgage = Image.frombuffer(
                    "RGBA", (self.width_frame, self.height_frame), self.new_image, "raw", "BGRA", 0, 1)
                self.image_arr =  cv2.cvtColor(np.array(imgage), cv2.COLOR_RGB2BGR)
                ret, buf = cv2.imencode(".jpeg", self.image_arr)
                self.image_bytes = buf.tobytes()
            except:
                pass

    def _play_stream_process(self):
        self._state = CameraState.PLAYING
        self.update_camera_status()
        logger.info(f"VLC Play Streaming: {self.rtsp_link}")
        self._player = self.vlc_instance.media_player_new()
        self._player.set_mrl(self.rtsp_link)
        self._player.audio_set_mute(True)

        # size in bytes when RV32
        size = self.width_frame * self.height_frame * 4

        # allocate buffer
        buf = (ctypes.c_ubyte * size)()
        # get pointer to buffer
        buf_p = ctypes.cast(buf, ctypes.c_void_p)

        CorrectVideoLockCb = ctypes.CFUNCTYPE(
            ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))

        @CorrectVideoLockCb
        def _lockcb(opaque, planes):
            planes[0] = buf_p

        @vlc.CallbackDecorators.VideoDisplayCb
        def set_current_buffer(opaque, picture):
            self.new_image=buf
            self.stop.set()

        vlc.libvlc_video_set_callbacks(self._player, _lockcb, None, set_current_buffer, None)
        self._player.video_set_format("RV32", self.width_frame, self.height_frame, self.width_frame * 4)
        self._player.play()
        time.sleep(stream_config.RECONNECT_INTERVAL)
        while self._is_running_play_stream:
            player_state = self._player.get_state()
            if vlc.State.Playing != player_state:
                logger.warning(f"VLC State {player_state}: {self.rtsp_link}")
                self._state = CameraState.DISCONNECT
            if vlc.State.Ended == player_state:
                self._player.set_mrl(self.rtsp_link)
                vlc.libvlc_video_set_callbacks(self._player, _lockcb, None, set_current_buffer, None)
                self._player.video_set_format("RV32", self.width_frame, self.height_frame, self.width_frame * 4)
                self._player.play()
                
            self.update_camera_status()
            
            time.sleep(5)

    def get_state(self):
        return self._state

    def get_current_frame(self):
        return self.image_arr
 
    def get_streaming_iterator(self):
        """A generator for the image."""
        header = "--jpgboundary\r\nContent-Type: image/jpeg\r\n"
        prefix = ""
        while True:
            frame = self.get_current_frame()
            _, jpeg = cv2.imencode(
                ".jpg",
                frame,
                params=(cv2.IMWRITE_JPEG_QUALITY, 70),
            )
            msg = (
                prefix
                + header
                + "Content-Length: {}\r\n\r\n".format(len(jpeg.tobytes()))
            )

            yield (msg.encode("utf-8") + jpeg.tobytes())
            prefix = "\r\n"
            time.sleep(0.05)

    def get_lastframe_bytes(self):
        return self.image_bytes

    def stop_stream(self):
        self.stop.set()
        self._player.stop()
        self._is_running_decode = False
        self._is_running_play_stream = False