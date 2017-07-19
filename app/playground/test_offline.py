import sys
sys.path.insert(1, "app")

from modules.api import BluemixApi

api = BluemixApi()
cameraId = "test_camera"

api.queueOfflineImage("201702011201.jpg", "test_images")

# try uploading offline images once a minute
if api.offlineImagesQueued():
    try:
        api.uploadOfflineImages(cameraId)
    except Exception as e:
        print "Unable to upload offline images", e