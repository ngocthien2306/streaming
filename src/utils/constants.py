class CameraState:
    INIT: str = 'INIT'
    PLAYING: str = 'PLAYING'
    DISCONNECT: str = 'DISCONNECT'

class DatabaseConfig:
    DB_NAME: str = "cctv-ai"
    COLLECTION_NAME: str = "cameras"