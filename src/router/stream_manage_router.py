from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, Response

from utils import model
from utils.project_config import project_config
from services.stream_manage import StreamManage

router = APIRouter(prefix="/stream-manage")
stream_manage = StreamManage()

@router.post("/camera", response_model=model.Reponse[model.CameraResponse])
async def add_camera(camera: model.Camera):
    try:
        result = stream_manage.add_camera(camera)
        return {"data": result}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.delete("/camera/{camera_id}", response_model=model.Reponse[object])
async def delete_camera(camera_id: str):
    try:
        result = stream_manage.delete_camera(camera_id)
        return {"data": result}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/streaming/{camera_id}")
async def streaming(camera_id: str):
    if not project_config.ALLOW_SHOW_STREAM:
        raise HTTPException(
            status_code=403,
            detail="Not allow show stream"
        )
    if not stream_manage.check_camera_id_exist(camera_id):
        raise HTTPException(
            status_code=404,
            detail="Camera ID not found"
        )

    player = stream_manage.get_player_by_id(camera_id)
    return StreamingResponse(
        player.get_streaming_iterator(),
        media_type="multipart/x-mixed-replace;boundary=jpgboundary"
    )

@router.get("/lastframe/{camera_id}")
async def streaming(camera_id: str):
    if not project_config.ALLOW_SHOW_STREAM:
        raise HTTPException(
            status_code=403,
            detail="Not allow show stream"
        )
    if not stream_manage.check_camera_id_exist(camera_id):
        raise HTTPException(
            status_code=404,
            detail="Camera ID not found"
        )

    player = stream_manage.get_player_by_id(camera_id)
    return Response(
        player.get_lastframe_bytes(),
        media_type="image/png"
    )

@router.get("/camera/{camera_id}", response_model=model.Reponse[model.CameraResponse])
async def get_camera(camera_id: str):
    if not stream_manage.check_camera_id_exist(camera_id):
        raise HTTPException(
            status_code=404,
            detail="Camera ID not found"
        )
    return {"data": stream_manage.get_camera(camera_id)}

@router.get("/all-camera", response_model=model.ListReponse[model.CameraResponse])
async def get_all_camera():
    return {"data": list(stream_manage.get_all_cameras())}

@router.post("/output/{module_id}")
async def post_img(request: Request, module_id: str):
    data: bytes = await request.body()
    stream_manage.post_output(data, module_id)
    return

@router.get("/output/{module_id}")
async def post_img(module_id: str):
    return StreamingResponse(
        stream_manage.get_output(module_id),
        media_type="multipart/x-mixed-replace;boundary=jpgboundary"
    )