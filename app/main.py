import cv2
from datetime import *
import json
import os
from copy import deepcopy
import thread

from modules.detect_motion import MotionDetector
from modules.camera import Camera
from modules.config import *
from modules.api import BluemixApi
from modules.api_thread import BluemixApiThread
from modules.alarm import Alarm
from modules.iot import WatsonIoTApi

# Callback from API uploader
def response_callback(response, error):
    if response is not None:
        print response.text

        if response.status_code == 200:
            # check what the API says we should do
            result = json.loads(response.text)
            if result['rule'] == "1":
                # raise the alarm!
                alarm.raiseAlarm()
            else:
                # false alarm
                pass
        else:
            alarm.fallbackPlan(None, 'Response code from API was not 200')
    
    if error is not None:
        # call failed, so queue image for later upload
        api.queueOfflineImage(filename)
        alarm.fallbackPlan(boxes, e.message)

# Callback from IoT publisher
def iot_callback(command):
    print "iot_callback : "
    print command.data
    forced_image = cam.grabFrame()
    fname = "tmp/"+datetime.now().strftime("%Y%m%d%H%M%S")+"_snapshot.jpg"
    #TODO only write it to disk, availe API to upload it and communicate it to the cloud
    cv2.imwrite(fname, forced_image)


if __name__ == "__main__":
    config = read_config('config.yml')

    if config.has_key('camera_id'):
        cameraId = config['camera_id']
    else:
        cameraId = "double-vision-cam"

    md = MotionDetector()
    cam = Camera(rpiCam=config['rpi_camera'], cameraNum=config['camera_number'],
                 width=config['camera_width'], height=config['camera_height'],
                 fps=config['camera_fps'])
    api = BluemixApi()
    watsonIoT = WatsonIoTApi(iot_callback)
    lastApiCall = datetime.now()
    alarm = Alarm()

    if not os.path.isdir("tmp"):
        os.mkdir("tmp")

    cv2.namedWindow("preview")

    while True:
        image = cam.grabFrame()

        motion, boxes = md.detectMotion(image)
        if motion:
            # call the API, but not too often!
            if (datetime.now() - lastApiCall).seconds > 10:
                lastApiCall = datetime.now()

                filename = lastApiCall.strftime("%Y%m%d%H%M%S") + ".jpg"
                try:
                    # TODO: delete the file after done keeping it for debugging
                    # purpose
                    cv2.imwrite("tmp/" + filename, image)
                except Exception as e:
                    # unable to save image - maybe out of disk space!
                    alarm.fallbackPlan(boxes, "unable to save image")
                    continue

                try:
                    #publish the any motion dectected event to Watson IoT
                    # TODO run this in a thread otherwise it hangs when offline
                    watsonIoT.publish("{'TIMESTAMP':'"+lastApiCall.strftime("%Y%m%d%H%M%S" +"'}"))
                except Exception as e:
                    print "Error publishing to IoT", e
                    pass

                try:
                    print "Calling the API"
                    # none-blocking call for Camera detection to keep the
                    # camera rolling while uploading to cloud
                    thread1 = BluemixApiThread(
                        open("tmp/" + filename, 'rb'), cameraId, response_callback)
                    thread1.start()
                except Exception as e:
                    response_callback(None, e)

                # reset the motion detector as many frames were skipped
                md.reset()

            # for preview, add bounding boxes and text
            for (x, y, w, h) in boxes:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.putText(image, "Motion Detected", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 10)

        # try uploading offline images once a minute
        if api.offlineImagesQueued() and (datetime.now() - lastApiCall).seconds > 60:
            lastApiCall = datetime.now()
            try:
                api.uploadOfflineImages(cameraId)
            except Exception as e:
                print "Unable to upload offline images", e

        cv2.imshow("preview", image)

        key = cv2.waitKey(1) & 0xFF
        if key != 255:
            break

    watsonIoT.cleanup()
    cam.cleanup()
    cv2.destroyAllWindows()
