## Jul,17th, 20017.
## Author: M.Salah
## Team: Vision-Double (IBM Egypt - CIC Summer Internship)
## Title: Enchanced Face Detection Python Module
## Description:
#	FaceDetection Procedure function, used to be spawned as a separate process.

## ------------------------------------------------------------------------------------------------------
import cv2
import Queue
def DetectFace(ImageQ,verifyQ,scaleFactor,minNeighbors,minSize,FaceCascade,WorkerID):
	while True:
		frame=ImageQ.get()
		Image=frame.Image
		imgno=frame.imgno
		print("Thread FaceDetect: ",WorkerID," works on frame: ",imgno)
		GrayImage=cv2.cvtColor(Image,cv2.COLOR_BGR2GRAY)
		faces=FaceCascade.detectMultiScale(
		GrayImage,
		scaleFactor= scaleFactor,
		minNeighbors=minNeighbors,
		minSize=minSize,
		flags = cv2.cv.CV_HAAR_SCALE_IMAGE
		)
		#print('Found faces: '+str(len(faces))+' in frame '+str(imgno))
		for (x, y, w, h) in faces:
			cv2.rectangle(Image, (x, y), (x+w, y+h), (0, 0, 255), 2)
		frame.faces=len(faces)
		if len(faces) > 0:
			verifyQ.put(frame)
			#cv2.imwrite('./app/data/snapshots/'+'Faces'+str(len(faces))+'frame'+str(imgno)+'.png',Image)
			#print('Saved the captured frame: Faces'+str(len(faces))+'frame'+str(imgno)+'.png')
		ImageQ.task_done()
