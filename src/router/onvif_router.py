from fastapi import APIRouter, HTTPException

from utils import model
from services.onvif_service import get_rtsp

router = APIRouter(prefix="/onvif")

@router.post("/get-rtsp")
def get_stream_rtsp(camera_info: model.CameraInfo):
    rtsp_link = get_rtsp(
        camera_ip=camera_info.camera_ip,
        username=camera_info.username,
        password=camera_info.password
    )
    return {"data": rtsp_link}
