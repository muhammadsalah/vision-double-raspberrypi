import pprint
import ibmiotf.application
import ibmiotf.device
import time
import requests
import base64
import cv2
# To Do:
#	Provide the Bluemix IOT as configurables.
#
class WatsonIoTApi:
    def __init__(self, callback_method, organization="l3kk7q", deviceType="Double-Vision-Pi", deviceId="000c29cbd633", authToken="K25k+ue!&1bd49Xq(d",resturl="http://double-vision-hossam.mybluemix.net/image"):
	self.resturl=resturl
        try:
            appId= deviceId + "_receiver"
            authMethod = "token"
            deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
            self.deviceCli = ibmiotf.device.Client(deviceOptions)
            self.deviceCli.commandCallback = callback_method
            self.deviceCli.connect()
            
        except Exception as e:
            print (str(e))

    def publish(self, data):
        success = self.deviceCli.publishEvent("Double-Vision", "json", data, qos=0, on_publish=self.myOnPublishCallback)
	if not success:
		print("Not connected to Watson IoT")
		
    def myOnPublishCallback(data):
        print ("Data Published to Watson IoT")
        
    def cleanup(self):
        self.disconnect()
    
def WatsonThread(WatsonDataQ,Watson,TransmissionRate=10):
	while True:
		time.sleep(TransmissionRate)
		frame=WatsonDataQ.get()
		data={"d":{"objects":frame.objects,"faces":frame.faces}}
		with WatsonDataQ.mutex:
			WatsonDataQ.queue.clear()
		Watson.publish(data) # To WatsonIoT
		encodedimage=cv2.imencode('.jpeg',frame.Image)[1]
		b64image=base64.encodestring(encodedimage)
		json={"image64": "data:image/jpeg;base64,"+b64image}
		requests.post(Watson.resturl,json)	
		WatsonDataQ.task_done()
