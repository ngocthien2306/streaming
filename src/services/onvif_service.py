from onvif import ONVIFCamera

from utils.project_config import BASE_DIR

def get_rtsp(camera_ip, username, password):
    mycam = ONVIFCamera(camera_ip, 80, username, password, BASE_DIR + '/wsdl/')
    media_service = mycam.create_media_service()
    profiles = media_service.GetProfiles()
    token = profiles[0].token
    res = media_service.GetStreamUri({'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}, 'ProfileToken': token})
    rtsp_link = res.Uri
    rtsp_link = rtsp_link.split("rtsp://")[1]
    rtsp_link = f"rtsp://{username}:{password}{rtsp_link}"
    return rtsp_link