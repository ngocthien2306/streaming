import os
import json

from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class StreamConfig(BaseSettings):
    NETWORK_CACHING: int = os.getenv("NETWORK_CACHING", 1000)
    RECONNECT_INTERVAL: int = os.getenv("RECONNECT_INTERVAL", 100)

class ProjectConfig(BaseSettings):
    DEBUG: bool = True
    DOCS_TITLE: str = "Camera Service"
    CAMERA_SERVICE_PORT: int = 8000
    STREAM_ENGINE: str = os.getenv("STREAM_ENGINE", "VLC")
    ALLOW_SHOW_STREAM: bool = os.getenv("ALLOW_SHOW_STREAM", False)
    DB_URL: str = os.getenv("DB_URL", "mongodb://localhost:27017")
    MESSAGE_QUEUE_URL: str = os.getenv("MESSAGE_QUEUE_URL", "10.17.70.10:9092")
    MESSAGE_QUEUE_USERNAME: str = os.getenv("MESSAGE_QUEUE_USERNAME", "admin")
    MESSAGE_QUEUE_PASSWORD: str = os.getenv("MESSAGE_QUEUE_PASSWORD", "admin-secret")
    EVENT_LOGS_DOCUMENT: str = os.getenv("EVENT_LOGS_DOCUMENT")
    CAMERA_DOCUMENT: str = os.getenv("CAMERA_DOCUMENT")
    SERVER_DOCUMENT: str = os.getenv("SERVER_DOCUMENT")
    DB_NAME: str = os.getenv("DB_NAME")
    SERVER_BE_IP: str = os.getenv("SERVER_BE_IP")
    
project_config = ProjectConfig()
stream_config = StreamConfig()

print(project_config, stream_config)