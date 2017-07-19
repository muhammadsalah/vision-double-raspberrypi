import datetime
import os
import requests


class BluemixApi:

    def __init__(self, base_url="https://mea-vision-double.mybluemix.net/vision-double-web/rest/"):
        self.base_url = base_url

    def uploadImage(self, image, cameraId, eventTime=None):
        if eventTime is None:
            eventTime = datetime.datetime.now().utcnow()

        return requests.post(self.base_url + "frame/upload",
                             data={'cameraId': cameraId,
                                   'eventTime': eventTime.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
                             files={'file': image})

    def uploadOfflineImages(self, cameraId, directory="offline"):
        files = os.listdir(directory)
        for f in files:
            if f.endswith(".jpg"):
                try:
                    self.uploadOfflineImage(cameraId, f, directory)
                except Exception as e:
                    print "Unable to upload", f, e

    def uploadOfflineImage(self, cameraId, filename, directory="offline"):
        eventTime = datetime.datetime.strptime(filename, "%Y%m%d%H%M%S.jpg")
        if eventTime is None:
            return

        retVal = requests.post(self.base_url + "frame/offline-upload",
                               data={'cameraId': cameraId,
                                     'eventTime': eventTime.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
                               files={'file': open(directory + "/" + filename)})

        # remove the uploaded file, otherwise it will keep re-uploading
        os.remove(directory + "/" + filename)

        return retVal

    def queueOfflineImage(self, filename, srcDir="tmp", destDir="offline"):
        if not os.path.isdir(destDir):
            os.mkdir(destDir)
        os.rename(srcDir + "/" + filename, destDir + "/" + filename)

    def offlineImagesQueued(self, directory="offline"):
        if not os.path.isdir(directory):
            return False

        files = os.listdir(directory)
        if len(files) > 0: # TODO - check for valid jpg files rather than any file
            return True

        return False
