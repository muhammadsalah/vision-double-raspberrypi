import Image
import cv2
import numpy
import pywt
import sys
import Queue
##################################################################
## This code is being adopted into Vision Double Project
## Modified by Muhammad S. Masoud
##################################################################
## File: haar_blur.py
## Author: Vladimir Kulyukin
## This is my implementation, to the best of my understanding,
## of the method given in "Blur Detection for Digital Images
## Using Wavelet Transform" by Hanghang Tong, Mingjing Li, Hongjiang
## Zhang, Changshui Zhang.
##
## to run:
## 1) install numpy and pywt
##
## 2) >> haar_estimate_image_blur('some_image.png', 35, 0.01)
## The two numbers in two threasholds. The first threshold is
## the threshold used in the application of the haar rules (read
## the text of the paper for more details); the second threshold is
## the threshold used in computing the extent of bluriness. This function
## returns a 2-tuple: (Boolean, Float). The boolean indicates whether
## the image is blurred or not. The float is the bluriness extent of the image.
## The boolean classification is not that reliable. Using the blur extent
## appears to be more reliable.
##
## 3) >> haar_estimate_image_blur_extent('some_image.png', 35) is the same
## as the above function but returns only float indicating the blur extent
## of the image.
##
## bugs, suggestions, improvements to vladimir dot kulyukin at gmail dot com
##
##################################################################

def haar_compute_emaps_from_image(image):
    #image filename goes here
    image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im=Image.fromarray(image)
    imf=im.convert('F')
    ##print 'im size = ', numpy.shape(im)
    imary = numpy.asarray(imf)
    ##print 'uncropped image array size = ', numpy.shape(imary)
    ## Crop the image so that its size is divisible by 16.
    imh, imw = numpy.shape(imary)
    cropped_imary=imary[0:(imh/16)*16,0:(imw/16)*16]
    ##print 'cropped_ary size = ', numpy.shape(cropped_imary)
    ## STEP 1: Perform Haar wavelet transform to the original image
    ## and the decomposition level is 3. The result is a hierarchical
    ## pyramid-like structure.
    ## LL1 are the averages; LH1 are the horizontals;
    ## HL1 are the vertical changes; HH1 are the diagonal changes.
    LL1,(LH1,HL1,HH1)= pywt.dwt2(cropped_imary, 'haar')
    ## Another application of 2D haar to LL1
    LL2,(LH2,HL2,HH2)= pywt.dwt2(LL1, 'haar') 
    ## Another application of 2D haar to LL2
    LL3,(LH3,HL3,HH3)= pywt.dwt2(LL2, 'haar')
    ## STEP 2: Construct the edge map in each scale.
    ## LH1^2 = numpy.square(LH1), this squares each entry in an array.
    ## LH2^2 = numpy.square(LH2), this squares each entry in an array.
    ## LH3^3 = numpy.square(LH3), this squares each entry in an array
    ## The paper actually states that the formula is
    ## Emap(k, l) = square_root(LH1^2 + LH2^2 + LH3^2).
    ## The actual formulas used in the paper are:
    EMAP8x8 = numpy.sqrt(numpy.square(LH1)+numpy.square(HL1)+numpy.square(HH1))
    EMAP4x4 = numpy.sqrt(numpy.square(LH2)+numpy.square(HL2)+numpy.square(HH2))
    EMAP2x2 = numpy.sqrt(numpy.square(LH3)+numpy.square(HL3)+numpy.square(HH3))
    return (EMAP2x2, EMAP4x4, EMAP8x8)

## EMAX is a 2d array of maxvalues in every nxn window.
## STEP 3: compute EMAX1, EMAX2, EMAX3 where EMAX1 has a window size of 8x8,
## EMAX2 has a window size of 4x4, and EMAX3 has a window size of 2x2.
## EMAX represents the intensities of edges. It should be noted that
## EMAX1, EMAX2, EMAX3 are all of the same dimension.
def haar_compute_emax(emap, dimx, dimy, n):
    ##print "dimy=", dimy, "dimx=", dimx
    emax = numpy.ndarray(shape=(dimx/n, dimy/n), dtype=float)
    ## print numpy.shape(emax)
    curr_row = 0
    curr_col = 0
    for row in xrange(0, dimx - n + 1, n):
        curr_col = 0
        for col in xrange(0, dimy - n + 1, n):
            ## print row, col
            ## print emap[row:row+n, col:col+n]
            ## maxval = numpy.max(emap[row:row+n, col:col+n])
            maxval = 0
            for max_row in xrange(row, row+n):
                for max_col in xrange(col, col+n):
                   if ( emap[max_row][max_col] > maxval ):
                       maxval = emap[max_row][max_col]
            emax[curr_row][curr_col] = maxval
            curr_col += 1
        curr_row += 1
    return emax

## These lists are for debugging purposes only:
DIRAC_ASTEP_LIST  = []
ROOF_GSTEP_LIST   = []
BLURRED_ROOF_LIST = []
EDGE_LIST = []
## emap1, emap2, and emap3 are of size dimx x dimy
def haar_compute_image_edge_stats_from_emax(emax1, emax2, emax3, dimx, dimy, thresh):
    NUM_EDGES       = 0
    NUM_DIRAC_ASTEP = 0
    NUM_ROOF_GSTEP  = 0
    NUM_BLURRED_ROOF_GSTEP = 0
    global DIRAC_ASTEP_LIST  ## this is for debugging purposes only
    global ROOF_GSTEP_LIST   ## this is for debugging purposes only
    global BLURRED_ROOF_LIST ## this is for debugging purposes only
    global EDGE_LIST         ## this is for debugging purposes only
    DIRAC_ASTEP_LIST  = []
    ROOF_GSTEP_LIST   = []
    BLURRED_ROOF_LIST = []
    EDGE_LIST         = []
    for row in xrange(0, dimx):
        for col in xrange(0, dimy):
            ROOF_GSTEP_FLAG = False
            ## RULE 1: If Emax1(k,l)>threshold or Emax2(k,l)>threshold or Emax3(k,l)>threshold
            if rule_1(emax1, emax2, emax3, row, col, thresh):
                NUM_EDGES += 1
                EDGE_LIST.append((row,col))
                ## print 'RULE 1'
                ## print (row,col)
                ## print 'RULE 1'
                ## RULE 2: if Emax1(k, l)>Emax2(k,l)>Emax3(k,l), then (k, l) is Dirac/AStep
                if rule_2(emax1, emax2, emax3, row, col, thresh):
                    NUM_DIRAC_ASTEP += 1
                    DIRAC_ASTEP_LIST.append((row,col))
                    ## print 'RULE 2'
                ## RULE 3: If Emax1(k,l)<Emax2(k,l)<Emax3(k,l), then (k,l) is Roof/GStep    
                elif rule_3(emax1, emax2, emax3, row, col, thresh):
                    ROOF_GSTEP_FLAG = True
                    NUM_ROOF_GSTEP += 1
                    ROOF_GSTEP_LIST.append((row,col))
                    ## print 'RULE 3'
                ## RULE 4: If Emax2(k,l)>Emax1(k,l) and Emax2(k,l)>Emax3(k,l), then (k,l) is Roof
                elif rule_4(emax1, emax2, emax3, row, col, thresh):
                    ROOF_GSTEP_FLAG = True
                    NUM_ROOF_GSTEP += 1
                    ROOF_GSTEP_LIST.append((row,col))
                    ## print 'RULE 4'
                ## RULE 5: If Emax1(k,l)<threshold and (k,l) is Roof/GStep, then (k,l) is blurred
                if rule_5(emax1, row, col, thresh, ROOF_GSTEP_FLAG):
                    NUM_BLURRED_ROOF_GSTEP += 1
                    BLURRED_ROOF_LIST.append((row,col))
                    ## print 'RULE 5'
    return (NUM_EDGES, NUM_DIRAC_ASTEP, NUM_ROOF_GSTEP, NUM_BLURRED_ROOF_GSTEP)

## Is (row,col) an edge?
def rule_1(emax1, emax2, emax3, row, col, thresh):
    return (emax1[row][col]>thresh) or (emax2[row][col]>thresh) or (emax3[row][col]>thresh)

## Is (row, col) a Dirac or AStep?
def rule_2(emax1, emax2, emax3, row, col, thresh):
    return (emax1[row][col] > emax2[row][col]) and (emax2[row][col] > emax3[row][col])

## Is (row, col) a Roof or GStep?
def rule_3(emax1, emax2, emax3, row, col, thresh):
    return (emax1[row][col]<emax2[row][col]) and (emax2[row][col]<emax3[row][col])

## Is (row, col) a Roof?
def rule_4(emax1, emax2, emax3, row, col, thresh):
    return ( emax2[row][col] > emax1[row][col] ) and ( emax2[row][col] > emax3[row][col] )

## Is (row, col) in a blurred image?
def rule_5(emax1, row, col, thresh, roof_gstep_flag):
    return ( roof_gstep_flag == True ) and ( emax1[row][col] < thresh )

## This is a tool function for computing emaxes.
def haar_compute_emaxes_from_image(image, haar_thresh):
    EMAP2x2, EMAP4x4, EMAP8x8 = haar_compute_emaps_from_image(image)
    dimx1, dimy1 = numpy.shape(EMAP8x8)
    EMAX1 = haar_compute_emax(EMAP8x8, dimx1, dimy1, 8)
    ##print 'EMAX1', numpy.shape(EMAX1)
    dimx2, dimy2 = numpy.shape(EMAP4x4)
    EMAX2 = haar_compute_emax(EMAP4x4, dimx2, dimy2, 4)
    ##print 'EMAX2', numpy.shape(EMAX2)
    dimx3, dimy3 = numpy.shape(EMAP2x2)
    EMAX3 = haar_compute_emax(EMAP2x2, dimx3, dimy3, 2)
    ##print 'EMAX3', numpy.shape(EMAX3)
    return EMAX1, EMAX2, EMAX3
                                                     
def haar_estimate_image_blur(image, haar_thresh, min_zero_thresh):
    EMAX1, EMAX2, EMAX3 = haar_compute_emaxes_from_image(image, haar_thresh)
    dimx, dimy = numpy.shape(EMAX1)
    ##print 'dimx=', dimx, 'dimy=', dimy
    NUM_EDGES, NUM_DIRAC_ASTEP, NUM_ROOF_GSTEP, NUM_BLURRED_ROOF_GSTEP =\
               haar_compute_image_edge_stats_from_emax(EMAX1, EMAX2, EMAX3, dimx, dimy, haar_thresh)
    ## What happens if there are no DIRAC or ASTEP edges. Then
    ## PER is 0.
    ## Take care of the case when NUM_EDGES == 0.
    PER = float(NUM_DIRAC_ASTEP)/NUM_EDGES
    BLUR_EXTENT = 0
    if ( NUM_ROOF_GSTEP > 0 ):
        BLUR_EXTENT = float(NUM_BLURRED_ROOF_GSTEP)/NUM_ROOF_GSTEP
    else:
        ## There are no roof or gsteps
        BLUR_EXTENT = NUM_BLURRED_ROOF_GSTEP/NUM_EDGES
    is_blurred = True
    #print 'NUM_ROOF_GSTEP = ', NUM_ROOF_GSTEP
    #print 'NUM_EDGES = ', NUM_EDGES
    #print 'NUM_DIRAC_ASTEP = ', NUM_DIRAC_ASTEP
    #print 'NUM_BLURRED_ROOF_GSTEP = ', NUM_BLURRED_ROOF_GSTEP
    #print 'PER = ', PER
    #print 'BLUR_EXTENT = ', BLUR_EXTENT
    if PER > min_zero_thresh: 
        is_blurred = False
    return (is_blurred, BLUR_EXTENT)


def haar_estimate_image_blur_extent(image, haar_thresh):
    EMAX1, EMAX2, EMAX3 = haar_compute_emaxes_from_image(image, haar_thresh)
    dimx, dimy = numpy.shape(EMAX1)
    ##print 'dimx=', dimx, 'dimy=', dimy
    NUM_EDGES, NUM_DIRAC_ASTEP, NUM_ROOF_GSTEP, NUM_BLURRED_ROOF_GSTEP =\
               haar_compute_image_edge_stats_from_emax(EMAX1, EMAX2, EMAX3, dimx, dimy, haar_thresh)
    ## What happens if there are no DIRAC or ASTEP edges. Then
    ## PER is 0.
    ## Take care of the case when NUM_EDGES == 0.
    PER = float(NUM_DIRAC_ASTEP)/NUM_EDGES
    BLUR_EXTENT = 0
    if ( NUM_ROOF_GSTEP > 0 ):
        BLUR_EXTENT = float(NUM_BLURRED_ROOF_GSTEP)/NUM_ROOF_GSTEP
    else:
        ## There are no roof or gsteps
        BLUR_EXTENT = NUM_BLURRED_ROOF_GSTEP/NUM_EDGES
    is_blurred = True
    print 'NUM_ROOF_GSTEP = ', NUM_ROOF_GSTEP
    print 'NUM_EDGES = ', NUM_EDGES
    print 'NUM_DIRAC_ASTEP = ', NUM_DIRAC_ASTEP
    print 'NUM_BLURRED_ROOF_GSTEP = ', NUM_BLURRED_ROOF_GSTEP
    print 'PER = ', PER
    print 'BLUR_EXTENT = ', BLUR_EXTENT
    #if PER > min_zero_thresh: 
    #    is_blurred = False
    return BLUR_EXTENT

def haar_blur_test(image, haar_thresh, min_zero_thresh):
    is_blurred, BLUR_EXTENT = haar_estimate_image_blur(image, haar_thresh, min_zero_thresh)
    BLUR_EXTENT_01 = haar_estimate_image_blur_extent(image, haar_thresh)
    print is_blurred, BLUR_EXTENT
    print BLUR_EXTENT_01
####################################################################
# Vision Double Development Code:
def DetectBlur(verifyQ,WatsonDataQ, haar_thresh, min_zero_thresh,WorkerID):
	while True:
		frame=verifyQ.get()
		Image=frame.Image
		imgno=frame.imgno
		print("Thread BlurDetect: ",WorkerID," works on frame: ",imgno)
		is_blurred, blur_extent=haar_estimate_image_blur(Image,haar_thresh,min_zero_thresh)
		frame.isblur=is_blurred
		frame.blurextent=blur_extent
		if not is_blurred:
			cv2.imwrite('./app/data/snapshots/'+'NoBlurFaces'+'frame'+str(imgno)+'.png',Image)
			WatsonDataQ.put(frame)
		else:
			if is_blurred and blur_extent<0.2:
				cv2.imwrite('./app/data/snapshots/'+'BlurFaces'+'frame'+str(imgno)+'.png',Image)
				#WatsonDataQ.put(frame)

		verifyQ.task_done()	
