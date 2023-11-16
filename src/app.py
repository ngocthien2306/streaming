import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.logging_system import logger
from utils.project_config import project_config
from router.docs_router import add_docs_router
from router import stream_manage_router, onvif_router


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


@app.get("/all-thread")
def all_thread():
    import threading
    threads = []
    for thread in threading.enumerate(): 
        threads.append(thread.name)
    return threads


if __name__ == '__main__':
    logger.info(f"Starting Camera Service - Config: {project_config.dict()}")
    uvicorn.run(app, host="172.20.10.2", port=project_config.CAMERA_SERVICE_PORT)