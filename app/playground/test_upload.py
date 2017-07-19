import requests

# date format: yyyy-MM-dd'T'HH:mm:ss.SSSX

r = requests.post('https://mea-vision-double.mybluemix.net/vision-double-web/rest/frame/upload', 
    data={'cameraId': 'double-vision-cam', 'eventTime': '2016-01-10T13:00:00.000Z'},
    files={'file': open('test_images/face-only.jpg', 'rb')})

print r.text