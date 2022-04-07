import numpy as np
import random
import math

def fillLEDs(LEDArray, Color1):
    for i in range(len(LEDArray)):
        LEDArray[i] = Color1
    pass

def alternateLEDs(LEDArray, Color1, offset):
    for i in range(len(LEDArray)):
        if i % 2 == offset:
            LEDArray[i] = Color1
    pass

def randomFillLEDs(LEDArray):
    for i in range(len(LEDArray)):
        LEDArray[i] = [np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)]
    pass

#Define a function that fades from one color to the other, across the length of the input array
#inputs: LEDArray, Color1, Color2
def fadeLEDs(LEDArray, Color1, Color2):
    for i in range(len(LEDArray)):
        LEDArray[i] = [
            int(Color1[0] + ((Color2[0] - Color1[0]) / len(LEDArray)) * i),
            int(Color1[1] + ((Color2[1] - Color1[1]) / len(LEDArray)) * i),
            int(Color1[2] + ((Color2[2] - Color1[2]) / len(LEDArray)) * i),
        ]
    pass

#This was an absolute pain in my ass
def segmentedColor(LEDArray, ColorArray, percentage = 0.5):
    WorkingArray = np.copy(LEDArray)
    nonFullSegmentLength = 0
    #ensure that the array can be divided by the number of colors, and if it cant, then just use the last color
    if len(WorkingArray) % len(ColorArray) != 0:
        #store the length of non full segments
        nonFullSegmentLength = len(WorkingArray) % len(ColorArray)
        #resize the array to be divisible by the number of colors
        WorkingArray = WorkingArray[:len(WorkingArray) - (len(WorkingArray) % len(ColorArray))]
    #split WorkingArray into as many colors as there are in ColorArray
    WorkingArray = np.split(WorkingArray, len(ColorArray))
    #for each color in ColorArray, fill the corresponding WorkingArray with that color
    for i in range(len(ColorArray)):
        fadeToColor(WorkingArray[i], ColorArray[i], percentage)

    #concatenate the WorkingArray into one array
    WorkingArray = np.concatenate(WorkingArray)
    #resize the array to be the original length by adding the non full segment length to the end using numpy
    #Ensure that the new values are still (r, g ,b) format
    WorkingArray = np.resize(WorkingArray, (len(WorkingArray) + nonFullSegmentLength, 3))

    #make the pixels missed by the split the same color as the last color in ColorArray
    for i in range(len(WorkingArray)):
        if i >= len(WorkingArray) - nonFullSegmentLength:
            #get the last color in ColorArray
            lastColor = ColorArray[len(ColorArray) - 1]
            #fill the WorkingArray with the last color
            WorkingArray[i] = [lastColor[0], lastColor[1], lastColor[2]]
    #copy the WorkingArray back to the original LEDArray
    np.copyto(LEDArray, WorkingArray)
    pass

#define a function to shift the entire array to the left or right
def shiftLEDs(LEDArray, offset):
    np.copyto(LEDArray, np.roll(LEDArray, round(offset) * 3))
    pass

#define a function that takes in an LEDArray and takes each pixel, averages it with the pixel to its left, and right, and stores that in a temp array before modifiying the original LEDArray
#inputs: LEDArray, recursions
#recursions is the number of times the function is run on the temp array
def averageLEDs(LEDArray, recursions):
    #copy the array to left and right
    LEDArrayLeft = np.copy(LEDArray)
    LEDArrayRight = np.copy(LEDArray)
    #create a temp array merged from left, original, and right
    LEDArrayTemp = np.concatenate((LEDArrayLeft, LEDArray, LEDArrayRight))
    #average each pixel in the temp array with the pixel to its left and right and dont include the first and last pixels
    for i in range(1, len(LEDArrayTemp) - 1):
        LEDArrayTemp[i] = [
            (LEDArrayTemp[i - 1][0] + LEDArrayTemp[i][0] + LEDArrayTemp[i + 1][0]) / 3,
            (LEDArrayTemp[i - 1][1] + LEDArrayTemp[i][1] + LEDArrayTemp[i + 1][1]) / 3,
            (LEDArrayTemp[i - 1][2] + LEDArrayTemp[i][2] + LEDArrayTemp[i + 1][2]) / 3,
        ]
    #take only the middle of the array from the end of the left and beginning of the right
    LEDArrayTemp = LEDArrayTemp[len(LEDArrayLeft) : len(LEDArrayLeft) + len(LEDArray)]
    #run the function recursively
    if recursions > 0:
        averageLEDs(LEDArrayTemp, recursions - 1)
    #copy the temp array back to the original LEDArray
    np.copyto(LEDArray, LEDArrayTemp)
    pass

#Define a version of the averageLEDs function that does not wrap around the edges
def averageLEDsNoWrap(LEDArray, recursions):
    LEDArrayTemp = np.copy(LEDArray)
    #average each pixel in the temp array with the pixel to its left and right and dont include the first and last pixels
    for i in range(1, len(LEDArrayTemp) - 1):
        LEDArrayTemp[i] = [
            (LEDArrayTemp[i - 1][0] + LEDArrayTemp[i][0] + LEDArrayTemp[i + 1][0]) / 3,
            (LEDArrayTemp[i - 1][1] + LEDArrayTemp[i][1] + LEDArrayTemp[i + 1][1]) / 3,
            (LEDArrayTemp[i - 1][2] + LEDArrayTemp[i][2] + LEDArrayTemp[i + 1][2]) / 3,
        ]
    #run the function recursively
    if recursions > 0:
        averageLEDsNoWrap(LEDArrayTemp, recursions - 1)
    #copy the temp array back to the original LEDArray
    np.copyto(LEDArray, LEDArrayTemp)
    pass


def percentageFillLEDs(LEDArray, Color1, percentage, mirror = False):
    for i in range(len(LEDArray)):
        if not mirror:
            if i < (len(LEDArray) * percentage):
                LEDArray[i] = Color1
        else:
            if i > (len(LEDArray) * (1 - percentage)):
                LEDArray[i] = Color1
    pass

def percentageFillLEDsMirrored(LEDArray, Color1, percentage):
    percentageFillLEDs(LEDArray, Color1, percentage / 2)
    percentageFillLEDs(LEDArray, Color1, percentage / 2, True)

def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx
    return h, s, v

def hsv_to_rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

def subtractTuples(tuple1, tuple2):
    return (tuple1[0] - tuple2[0], tuple1[1] - tuple2[1], tuple1[2] - tuple2[2])

def addTuples(tuple1, tuple2):
    return (tuple1[0] + tuple2[0], tuple1[1] + tuple2[1], tuple1[2] + tuple2[2])

def scaleTuple(tuple1, scale):
    return (tuple1[0] * scale, tuple1[1] * scale, tuple1[2] * scale)

def lerpBetweenTuples(tuple1, tuple2, scale):
    return addTuples(scaleTuple(subtractTuples(tuple2, tuple1), scale), tuple1)

def limitRGB(rgb):
    if rgb[0] > 255:
        rgb[0] = 255
    if rgb[1] > 255:
        rgb[1] = 255
    if rgb[2] > 255:
        rgb[2] = 255
    if rgb[0] < 0:
        rgb[0] = 0
    if rgb[1] < 0:
        rgb[1] = 0
    if rgb[2] < 0:
        rgb[2] = 0
    return rgb

#define a function that takes in a LEDArray and changes the array to be closer to the desired color
#Percentage is a float from 0 to 1
def fadeToColor(LEDArray, Color1, percentage):
    #prevent percentage from going over 1
    if percentage > 1:
        percentage = 1
    #prevent percentage from going under 0
    if percentage < 0:
        percentage = 0
    for i in range(len(LEDArray)):
        LEDArray[i] = lerpBetweenTuples(LEDArray[i], Color1, percentage)
        LEDArray[i] = limitRGB(LEDArray[i])
    pass

#define a function that takes in a LEDArray and uses a percentage to fade between two different colors
def fadeBetweenColors(LEDArray, Color1, Color2, percentage):
    #prevent percentage from going over 1
    if percentage > 1:
        percentage = 1
    #prevent percentage from going under 0
    if percentage < 0:
        percentage = 0
    for i in range(len(LEDArray)):
        LEDArray[i] = lerpBetweenTuples(Color1, Color2, percentage)
        LEDArray[i] = limitRGB(LEDArray[i])
    pass

def randomStars(LEDArray, color):
    for i in range(len(LEDArray)):
        #randomly choose true or false
        if random.randint(0, 6) == 1:
            LEDArray[i] = color
    pass