'''
To use, make sure to run:

pip install pdf2image
'''

import sys
import os
from pdf2image import convert_from_path
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

Image.MAX_IMAGE_PIXELS = None #this is bad to do usually bc of zipbombs but this works

print("Running convert_from_path()...")
pages = convert_from_path('SERENGETI DP.pdf', 500)


print("Saving page(s)...")
for page in pages:
    page.save('out.png', 'PNG')

print("pytesseract tests...")
outputfile = open("text.txt", "w")
outputfile.write(pytesseract.image_to_boxes(Image.open('out.png')))
outputfile.close()
