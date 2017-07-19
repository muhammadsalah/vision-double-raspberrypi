import time
import sys
import pprint
import ibmiotf.application
import ibmiotf.device

class WatsonIoTApi:
    def __init__(self, callback_method, organization="245e5o", deviceType="Camera", deviceId="b827eb71e29bdv", authToken="VISION_DOUBLE_CAMERA"):
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
        success = self.deviceCli.publishEvent("MOTION_DETECTED", "json", data, qos=0, on_publish=self.myOnPublishCallback)
	if not success:
		print("Not connected to IoTF")
		
    def myOnPublishCallback(data):
        print data
        
    def cleanup(self):
        self.disconnect()
    
    
