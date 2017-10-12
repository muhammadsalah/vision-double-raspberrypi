import cv2
# TO DO:
#	Separate the parameters (The so called magic numbers)
# 	to a parameter file or expose them to the user for fine
# 	tunning purposes.
#
class MotionDetector:
    def __init__(self):
        self.reset()

    def reset(self):
	self.min_area=500
	self.motionsense=0
        self.firstFrame = None
        self.framesOfMotion = 0

    def detectMotion(self, image):
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grey = cv2.GaussianBlur(grey, (21, 21), 0)
        
        if self.firstFrame is None:
            self.firstFrame = grey

        # compute the absolute difference between the current frame and
        # first frame
        frameDelta = cv2.absdiff(self.firstFrame, grey)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        self.firstFrame = grey

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    
        # loop over the contours
        frameMotionDetected = False
        boundingBoxes = []
        for c in cnts:
            if cv2.contourArea(c) < self.min_area:
                continue; # ignore small contours

            # compute the bounding box for the contour
            (x, y, w, h) = cv2.boundingRect(c)

            # filter out small bounding boxes
            if w > 20 and h > 50:
                boundingBoxes.append((x, y, w, h))
                frameMotionDetected = True                

        if frameMotionDetected:
            self.framesOfMotion += 1
        else:
            self.framesOfMotion = 0

        # filter out spurious motion
        if self.framesOfMotion > self.motionsense:
            return True, boundingBoxes
        
        return False, None
        
