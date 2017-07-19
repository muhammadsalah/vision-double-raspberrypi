import requests
import datetime
import threading
from api import BluemixApi

class BluemixApiThread (threading.Thread):
    def __init__(self, image, cameraId, callback,eventTime=None):
        threading.Thread.__init__(self)
        self.image = image
        self.cameraId = cameraId
        self.eventTime = eventTime
        self.api = BluemixApi()
        self.callback = callback
                                    
    def run(self):
        try:
            response = self.api.uploadImage(self.image, self.cameraId, self.eventTime)
            self.callback(response, None)
        except Exception as e:
            self.callback(None, e)
        