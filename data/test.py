from PIL import Image
from pytesseract import image_to_string
import sys
import re
import os


image_data = [
    {
        'bounds': [0.280449, 0.034227, 0.200321, 0.06275],
        'options': [
            {'pattern': '.*K(1|I|l)$', 'result': 'K1'},
            {'pattern': '.*K4', 'result': 'K4'},
            {'pattern': '.*K3', 'result': 'K3'},
        ]
    },
    {
        'bounds': [0.264423, 0.028523, 0.184295, 0.06275],
        'options': [
            {'pattern': '.*K(1|I|l)3', 'result': 'K13'},
            {'pattern': '.*K2', 'result': 'K2'},
        ]
    },
    {
        'bounds': [0.761217948717949, 0.246434683399886, 0.128205128205128, 0.0570450656018254],
        'options': [
            {'pattern': '.*PAB', 'result': 'PAB'},
            {'pattern': '.*WOB', 'result': 'WOB'},
        ]
    },
    {
        'bounds': [0.833333333333333, 0.0376497432972048, 0.112179487179487, 0.0228180262407302],
        'options': [
            {'pattern': '.*K(1|I|l)(1|I|l)', 'result': 'K11'},
        ]
    },
    {
        'bounds': [0.240384615384615, 0.0456360524814604, 0.16025641025641, 0.0342270393610953],
        'options': [
            {'pattern': '.*K(1|I|l)9', 'result': 'K19'},
            {'pattern': '.*K(Z|2)(0|O)', 'result': 'K20'},
        ]
    },
    {
        'bounds': [0.0240384615384615, 0.0285225328009127, 0.192307692307692, 0.0713063320022818],
        'options': [
            {'pattern': '.*K(1|I|l)5', 'result': 'K15'},
            {'pattern': '.*K(1|I|l)6', 'result': 'K16'},
        ]
    },
    {
        'bounds': [0.269230769230769, 0.220764403879064, 0.144230769230769, 0.0342270393610953],
        'options': [
            {'pattern': '.*WOB', 'result': 'WOB(Amend)'},
        ]
    }


]
devnull = open(os.devnull, 'w')


files = os.listdir(".")
for file in files:
    #(file)
    fn, ext = os.path.splitext(file)
    #print(ext)
    if ext != ".jpeg" and ext != '.png':
        continue
    #print("========================", file=sys.stderr)
    #print("Analyse " + file, file=sys.stderr)
    found = False
    image = Image.open(file)
    for item in image_data:
        left = int(image.width * item['bounds'][0])
        top = int(image.height * item['bounds'][1])
        width = int(image.width * item['bounds'][2])
        height = int(image.height * item['bounds'][3])
        cropped = image.crop((left, top, left + width, top + height))

        text = image_to_string(cropped)
        #print("    Text is: " + text, file=sys.stderr)

        for option in item['options']:
            m = re.match(option['pattern'], text)
            if m is not None:
                print("Image " + file + " is a " + option['result'], file=sys.stderr)
                found = True
                break
        if found:
            break
    if not found:
        print("Image " + file + " is a mystery", file=sys.stderr)


# image = Image.open(filename)
# left = int(image.width * 0.280449)
# top = int(image.height * 0.034227)
# width = int(image.width * 0.200321)
# height = int(image.height * 0.06275)
#
# image = image.crop((left, top, left + width, top + height))
#
# # image = image.crop((290, 55, 520, 145))
# image.save("crop.jpeg")
# text = image_to_string(image)
#
# print(text)