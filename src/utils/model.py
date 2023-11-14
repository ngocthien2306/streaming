from typing import Generic, TypeVar, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

M = TypeVar("M", bound=BaseModel)

class Camera(BaseModel):
    rtsp_link: str
    camera_id: str
    camera_name: str
    camera_location: str = ""
    frame_rate: int = 6
    output_width: int = 1280
    output_height: int = 720

class CameraInfo(BaseModel):
    camera_ip: str
    username: str
    password: str

class CameraResponse(Camera):
    state: str = "INIT"

class Reponse(GenericModel, Generic[M]):
    data: M
    status: str = "success"

class ListReponse(GenericModel, Generic[M]):
    data: List[M]
    status: str = "success"

