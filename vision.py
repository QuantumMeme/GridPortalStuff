'''
vision.py
David Pesin

Uses Google's Vision API to detect text in an image.

Returns the text in output.txt for the first pass, and output2.txt for the second
after rotating the image.
'''
# -*- coding: utf-8 -*-

import os
import sys
import cv2
import numpy as np

#for file selection
from tkinter import Tk
from tkinter.filedialog import askopenfilename

run = 0 # Counting to run twice

#Setting the file
Tk().withdraw()
name = askopenfilename(initialdir=os.getcwd(),
                       title="Select an image file.",
                       filetypes=[('image files', ('.jpg','.png','.tif','.bmp','.tiff'))])
print("\n", name, " selected.\n")
img = cv2.imread(name) #creating image
img2 = cv2.imread(name) #creating second image

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

#accounts for errors that come from encoding differences in read images
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

def rotate_image(mat, angle):
    """
    Rotates an image (angle in degrees) and expands image to avoid cropping
    """

    height, width = mat.shape[:2] # image shape has 3 dimensions
    image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0,0]) 
    abs_sin = abs(rotation_mat[0,1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat

def detect_text(path):
    """Detects text in the file."""
    print("\n##################################################")
    print("Encoding: ", sys.stdout.encoding)

    if(run == 0):
        open('output.txt', 'w').close() # clearing outputfiles
        open('output2.txt', 'w').close()

    from google.cloud import vision
    import io

    print("Creating client...")

    client = vision.ImageAnnotatorClient() # Creating client

    print("Opening file...")

    with io.open(path, 'rb') as image_file: # opening file
        content = image_file.read()

    image = vision.types.Image(content=content)

    print('Detecting text...')

    response = client.text_detection(image=image) #calls text_detection from the vision API
    texts = response.text_annotations 

    print("Writing to output.txt...")

    rects = 0 # counting number of iterations in below for-loop for each rectangle in final image

    printProgressBar(0, (len(texts)), prefix = 'Progress:', suffix = 'Complete', length = 50) #initial call to print 0% progress

    for text in texts:

        #text is outputted into the output files.
        if (run == 0):
            uprint(u'\n"{}"'.format(text.description), file=open("output.txt", "a"))
        else:
            uprint(u'\n"{}"'.format(text.description), file=open("output2.txt", "a"))

        counter = 0 #finding vertices of each word

        vertices = (['({},{})'.format(vertex.x, vertex.y) #all coordinates that are stored in the bounding polygon stored
                    for vertex in text.bounding_poly.vertices])
        
        if (run == 0):
            uprint(u'bounds: {}'.format(','.join(vertices)), file = open("output.txt", "a")) #printing the 4 vertices outlining the rectangle
        else:
            uprint(u'bounds: {}'.format(','.join(vertices)), file = open("output2.txt", "a"))

        polygon = [] # for fillConvexPoly() later

        for vertex in text.bounding_poly.vertices: #getting coordinates for cv2.rectangle()
            polygon.append((vertex.x, vertex.y))
            if (counter == 0):
                x1 = vertex.x
                y1 = vertex.y
            elif (counter == 2):
                x2 = vertex.x
                y2 = vertex.y
            counter += 1
        #rectangles surrounding text
        if (run == 0):
            if (rects == 0): #initial rectangle is in red
                color = (0,0,255)
            else: #remaining ones are in blue
                color = (255,0,0)
        else:
            if (rects == 0): #initial rectangle is in green
                color = (0,255,0)
            else: #remaining ones are in blue
                color = (255,0,0)

        cv2.rectangle(img, (x1,y1), (x2,y2), color, 2) #placing rectangles in image
        

        #removing text
        if(rects != 0):
            cv2.fillConvexPoly(img2, np.array(polygon, 'int32'), (255,255,255)) #whites out the text. TODO detect color

        printProgressBar(rects + 1, (len(texts)), prefix = 'Progress:', suffix = 'Complete', length = 50)

        rects += 1

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    if (run == 0):
        print("Writing temporary image with text removed...")
        cv2.imwrite("visionpyfiles/temp.png", img2)
    print("##################################################\n")

file_name = os.path.abspath(name)


print("Calling detect_text()!")
detect_text(file_name)

print("Rotating image 90 degrees!")
img2 = rotate_image(img2, 90)


run += 1 # next run

print("Calling detect_text()!")
detect_text("visionpyfiles/temp.png")

print("Rotating image 270 degrees!")
img2 = rotate_image(img2, 270)

print("Cleaning up temporary file...") 
os.remove("visionpyfiles/temp.png") #comment this out if you want to keep the image with the text removed

print("Writing final images...")
cv2.imwrite("visionpyfiles/finalimage.png", img) #writing image with rectangles
print("...done!")