import cv2
import numpy

flt_x_co = []

    #filter x coordinates
def fltr(x_co = []):
    x_co.sort()
    i=1
    st=0
    beg=0
    end=0
    large=0
    while i<len(x_co):
       if x_co[i] - x_co[st] > 200:
           if i-st > large:
               beg=st
               end=i-1
               large=end-beg+1
           st=i
       i = i+1
    if i-st > large:
	beg=st
	end=i-1
	
    print x_co
    flt_x_co=x_co[beg:end+1]
    return flt_x_co
    
i=0
print i
opencv_haystack = cv2.imread('capture.png')
opencv_needle =cv2.imread('template.png')

ngrey = cv2.cvtColor(opencv_needle, cv2.COLOR_BGR2GRAY)
hgrey = cv2.cvtColor(opencv_haystack, cv2.COLOR_BGR2GRAY)

	# build feature detector and descriptor extractor
hessian_threshold = 100
detector = cv2.SURF(hessian_threshold)
(hkeypoints, hdescriptors) = detector.detect(hgrey, None, useProvidedKeypoints = False)
(nkeypoints, ndescriptors) = detector.detect(ngrey, None, useProvidedKeypoints = False)

	# extract vectors of size 64 from raw descriptors numpy arrays
rowsize = len(hdescriptors) / len(hkeypoints)
if rowsize > 1:
    hrows = numpy.array(hdescriptors, dtype = numpy.float32).reshape((-1, rowsize))
    nrows = numpy.array(ndescriptors, dtype = numpy.float32).reshape((-1, rowsize))
    #print hrows.shape, nrows.shape
else:
    hrows = numpy.array(hdescriptors, dtype = numpy.float32)
    nrows = numpy.array(ndescriptors, dtype = numpy.float32)
    rowsize = len(hrows[0])

	# kNN training - learn mapping from hrow to hkeypoints index
samples = hrows
responses = numpy.arange(len(hkeypoints), dtype = numpy.float32)
	#print len(samples), len(responses)
knn = cv2.KNearest()
knn.train(samples,responses)

x_co=[]
cord={}
	# retrieve index and value through enumeration
for i, descriptor in enumerate(nrows):
	descriptor = numpy.array(descriptor, dtype = numpy.float32).reshape((1, rowsize))
	    #print i, descriptor.shape, samples[0].shape
	retval, results, neigh_resp, dists = knn.find_nearest(descriptor, 1)
	res, dist =  int(results[0][0]), dists[0][0]
	    #print res, dist

	if dist < 0.1:
		# draw matched keypoints in red color
		color = (0, 0, 255)
		x,y = hkeypoints[res].pt
        	xint = int(x)
        	yint = int(y)
		x_co.append(xint)
		cord[xint]=yint
	


flt_y_co=[]
flt_x_co = fltr(x_co)
print flt_x_co

    #average the filtered values
j=0
sum=0
while(j<len(flt_x_co)):
	sum = sum+flt_x_co[j]
	j = j+1
sum = sum/len(flt_x_co)
data = (sum - 640)

    #move according to the value of data
if data > 0:
    for i in 100:
        move_back()
        move_left()

else:
    for i in 100:
        move_back()
        move_right()
            

i = 0
while(i<len(flt_x_co)):
	flt_y_co.append(cord[flt_x_co[i]])
	center = (flt_x_co[i], flt_y_co[i])
	    # draw matched key points on haystack image
	cv2.circle(opencv_haystack,center,2,color,-1)
	i = i+1

cv2.imwrite('haystack.jpg',opencv_haystack)
cv2.waitKey(0)
cv2.destroyAllWindows()
