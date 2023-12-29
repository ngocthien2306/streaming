from utils.constants import CameraState
from utils.video_capture import VideoCaptureWrapper
import multiprocessing
import cv2 
import time
import threading
class CustomStreaming:
    def __init__(self, rtsp_link: str, producer, frame_rate: str, output_size=(1280, 720), camera_id: str = None) -> None:
        self.rtsp_link = rtsp_link
        self.frame_rate = frame_rate
        self.image_arr = None
        self.image_bytes = None
        self.width_frame, self.height_frame = output_size
        self._camera_id = camera_id
        self._video_capture = cv2.VideoCapture(rtsp_link)
        self._state = CameraState.INIT
        self.__enqueue = threading.Thread(target=self._run_camera, daemon=True)
        self.__enqueue.start()
        # self._run_camera()
        
    def _run_camera(self):
        
        try:
            while True:
                _, frame = self._video_capture.read()
                frame = cv2.resize(frame, (self.width_frame, self.height_frame))
                _, buf = cv2.imencode(".jpeg", frame.copy())
                self.image_arr = frame.copy()
                self.image_bytes = buf.tobytes()
                # cv2.imshow('frame', frame) 

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            pass

        finally:
            self._video_capture.release()
            cv2.destroyAllWindows()
         
    def get_state(self):
        return self._state
    
    def get_current_frame(self):
        return self.image_arr
        
    def get_lastframe_bytes(self):
        return self.image_bytes
    
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
