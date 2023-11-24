import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from utils.logging_system import logger
from utils.project_config import project_config
from router.docs_router import add_docs_router
from router import stream_manage_router, onvif_router
from pathlib import Path

app = FastAPI(
    version=1.0,
    title=project_config.DOCS_TITLE,
    debug=project_config.DEBUG, 
    docs_url=None, 
    redoc_url=None
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_docs_router(app)
app.include_router(stream_manage_router.router, tags=['Streaming'])
app.include_router(onvif_router.router, tags=['Onvif'])

app.mount("/public", StaticFiles(directory="C:/Users/delai/source/repos/Fence/logs"), name="public")

@app.get(
    path="/public"
)
async def post_media_file(file_path):
    video_path = Path("../logs/" + file_path)
    print(video_path)
    return FileResponse(video_path, media_type="video/mp4", headers={"Content-Type": "video/mp4"})

@app.get("/all-thread")
def all_thread():
    import threading
    threads = []
    for thread in threading.enumerate(): 
        threads.append(thread.name)
    return threads


if __name__ == '__main__':
    logger.info(f"Starting Camera Service - Config: {project_config.dict()}")
    uvicorn.run(app, host="26.30.0.242", port=project_config.CAMERA_SERVICE_PORT)