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

def subtractTuples(tuple1, tuple2):
    return (tuple1[0] - tuple2[0], tuple1[1] - tuple2[1], tuple1[2] - tuple2[2])

def addTuples(tuple1, tuple2):
    return (tuple1[0] + tuple2[0], tuple1[1] + tuple2[1], tuple1[2] + tuple2[2])

def scaleTuple(tuple1, scale):
    return (tuple1[0] * scale, tuple1[1] * scale, tuple1[2] * scale)

def lerpBetweenTuples(tuple1, tuple2, scale):
    return addTuples(scaleTuple(subtractTuples(tuple2, tuple1), scale), tuple1)

gammaCorrectionLookupTable = np.array(
    [
        [0, 0, 0],
        [0.01, 0.01, 0.01],
        [0.02, 0.02, 0.02],
        [0.03, 0.03, 0.03],
        [0.04, 0.04, 0.04],
        [0.05, 0.05, 0.05],
        [0.06, 0.06, 0.06],
        [0.07, 0.07, 0.07],
        [0.08, 0.08, 0.08],
        [0.09, 0.09, 0.09],
        [0.1, 0.1, 0.1],
        [0.11, 0.11, 0.11],
        [0.12, 0.12, 0.12],
        [0.13, 0.13, 0.13],
        [0.14, 0.14, 0.14],
        [0.15, 0.15, 0.15],
        [0.16, 0.16, 0.16],
        [0.17, 0.17, 0.17],
        [0.18, 0.18, 0.18],
        [0.19, 0.19, 0.19],
        [0.2, 0.2, 0.2],
        [0.21, 0.21, 0.21],
        [0.22, 0.22, 0.22],
        [0.23, 0.23, 0.23],
        [0.24, 0.24, 0.24],
        [0.25, 0.25, 0.25],
        [0.26, 0.26, 0.26],
        [0.27, 0.27, 0.27],
        [0.28, 0.28, 0.28],
        [0.29, 0.29, 0.29],
        [0.3, 0.3, 0.3],
        [0.31, 0.31, 0.31],
        [0.32, 0.32, 0.32],
        [0.33, 0.33, 0.33],
        [0.34, 0.34, 0.34],
        [0.35, 0.35, 0.35],
        [0.36, 0.36, 0.36],
        [0.37, 0.37, 0.37],
        [0.38, 0.38, 0.38],
        [0.39, 0.39, 0.39],
        [0.4, 0.4, 0.4],
        [0.41, 0.41, 0.41],
        [0.42, 0.42, 0.42],
        [0.43, 0.43, 0.43],
        [0.44, 0.44, 0.44],
        [0.45, 0.45, 0.45],
        [0.46, 0.46, 0.46],
        [0.47, 0.47, 0.47],
        [0.48, 0.48, 0.48],
        [0.49, 0.49, 0.49],
        [0.5, 0.5, 0.5],
        [0.51, 0.51, 0.51],
        [0.52, 0.52, 0.52],
        [0.53, 0.53, 0.53],
        [0.54, 0.54, 0.54],
        [0.55, 0.55, 0.55],
        [0.56, 0.56, 0.56],
        [0.57, 0.57, 0.57],
        [0.58, 0.58, 0.58],
        [0.59, 0.59, 0.59],
        [0.6, 0.6, 0.6],
        [0.61, 0.61, 0.61],
        [0.62, 0.62, 0.62],
        [0.63, 0.63, 0.63],
        [0.64, 0.64, 0.64],
        [0.65, 0.65, 0.65],
        [0.66, 0.66, 0.66],
        [0.67, 0.67, 0.67],
        [0.68, 0.68, 0.68],
        [0.69, 0.69, 0.69],
        [0.7, 0.7, 0.7],
        [0.71, 0.71, 0.71],
        [0.72, 0.72, 0.72],
        [0.73, 0.73, 0.73],
        [0.74, 0.74, 0.74],
        [0.75, 0.75, 0.75],
        [0.76, 0.76, 0.76],
        [0.77, 0.77, 0.77],
        [0.78, 0.78, 0.78],
        [0.79, 0.79, 0.79],
        [0.8, 0.8, 0.8],
        [0.81, 0.81, 0.81],
        [0.82, 0.82, 0.82],
        [0.83, 0.83, 0.83],
        [0.84, 0.84, 0.84],
        [0.85, 0.85, 0.85],
        [0.86, 0.86, 0.86],
        [0.87, 0.87, 0.87],
        [0.88, 0.88, 0.88],
        [0.89, 0.89, 0.89],
        [0.9, 0.9, 0.9],
        [0.91, 0.91, 0.91],
        [0.92, 0.92, 0.92],
        [0.93, 0.93, 0.93],
        [0.94, 0.94, 0.94],
        [0.95, 0.95, 0.95],
        [0.96, 0.96, 0.96],
        [0.97, 0.97, 0.97],
        [0.98, 0.98, 0.98],
        [0.99, 0.99, 0.99],
        [1, 1, 1],
    ]
)
#define a function to correct the gamma of an array
#LEDArray is an array of tuples
#return a gamma corrected array
def correctGamma(LEDArray):
    global gammaCorrectionLookupTable
    #create a new array to store the corrected values called gammaCorrectedArray filled with tuples initialized to 0
    gammaCorrectedArray = np.zeros((LEDArray.shape[0], LEDArray.shape[1]), dtype=np.uint8)
    #loop through the image and apply the gamma correction from the lookup table
    for i in range(len(gammaCorrectedArray)):
        gammaCorrectedArray[i] = np.multiply(LEDArray[i], gammaCorrectionLookupTable[i])
    #return the gamma corrected array
    return gammaCorrectedArray

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
        #LEDArray[i] = limitRGB(LEDArray[i])
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
        #LEDArray[i] = limitRGB(LEDArray[i])
    pass

def randomStars(LEDArray, color):
    for i in range(len(LEDArray)):
        #randomly choose true or false
        if random.randint(0, 6) == 1:
            LEDArray[i] = color
    pass