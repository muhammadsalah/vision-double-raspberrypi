import cv2
import zbar
from PIL import Image

def QRconfig(frame,scanner):
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    	pil = Image.fromarray(gray)
    	width, height = pil.size
    	raw = pil.tobytes()
    	image = zbar.Image(width, height, 'Y800', raw)
    	scanner.scan(image)
    	for symbol in image:
		f=open("./app/watsonconfig.txt","w+")
		f.write(symbol.data)
		return True
	return False
