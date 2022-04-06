import numpy as np
import random

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


#define a function that takes in a LEDArray and changes the array to be closer to the desired color
#ensure that the values do not go over 255 or under 0
#Percentage is a float from 0 to 1
def fadeToColor(LEDArray, Color1, percentage):
    #prevent percentage from going over 1
    if percentage > 1:
        percentage = 1
    #prevent percentage from going under 0
    if percentage < 0:
        percentage = 0
    for i in range(len(LEDArray)):
        #move the red value towards the desired colors red value
        if LEDArray[i][0] < Color1[0]:
            LEDArray[i][0] += (Color1[0] - LEDArray[i][0]) * percentage
        elif LEDArray[i][0] > Color1[0]:
            LEDArray[i][0] -= (LEDArray[i][0] - Color1[0]) * percentage
        #move the green value towards the desired colors green value
        if LEDArray[i][1] < Color1[1]:
            LEDArray[i][1] += (Color1[1] - LEDArray[i][1]) * percentage
        elif LEDArray[i][1] > Color1[1]:
            LEDArray[i][1] -= (LEDArray[i][1] - Color1[1]) * percentage
        #move the blue value towards the desired colors blue value
        if LEDArray[i][2] < Color1[2]:
            LEDArray[i][2] += (Color1[2] - LEDArray[i][2]) * percentage
        elif LEDArray[i][2] > Color1[2]:
            LEDArray[i][2] -= (LEDArray[i][2] - Color1[2]) * percentage

        #ensure that the values do not go over 255 or under 0
        if LEDArray[i][0] > 255:
            LEDArray[i][0] = 255
        if LEDArray[i][1] > 255:
            LEDArray[i][1] = 255
        if LEDArray[i][2] > 255:
            LEDArray[i][2] = 255
        if LEDArray[i][0] < 0:
            LEDArray[i][0] = 0
        if LEDArray[i][1] < 0:
            LEDArray[i][1] = 0
        if LEDArray[i][2] < 0:
            LEDArray[i][2] = 0
    pass

#define a function that takes in a LEDArray and uses a percentage to fade between two different colors
#ensure that the values do not go over 255 or under 0
def fadeBetweenColors(LEDArray, Color1, Color2, percentage):
    #prevent percentage from going over 1
    if percentage > 1:
        percentage = 1
    #prevent percentage from going under 0
    if percentage < 0:
        percentage = 0
    for i in range(len(LEDArray)):
        #change the led array as such to be closer to color 1 when percentage is 0 and closer to color 2 when percentage is 1. do not use the length of the LEDArray as the percentage
        LEDArray[i] = [
            int(Color1[0] + ((Color2[0] - Color1[0]) * percentage)),
            int(Color1[1] + ((Color2[1] - Color1[1]) * percentage)),
            int(Color1[2] + ((Color2[2] - Color1[2]) * percentage)),
        ]
        #ensure that the values do not go over 255 or under 0
        if LEDArray[i][0] > 255:
            LEDArray[i][0] = 255
        if LEDArray[i][1] > 255:
            LEDArray[i][1] = 255
        if LEDArray[i][2] > 255:
            LEDArray[i][2] = 255
        if LEDArray[i][0] < 0:
            LEDArray[i][0] = 0
        if LEDArray[i][1] < 0:
            LEDArray[i][1] = 0
        if LEDArray[i][2] < 0:
            LEDArray[i][2] = 0
    pass

def randomStars(LEDArray, color):
    for i in range(len(LEDArray)):
        #randomly choose true or false
        if random.randint(0, 6) == 1:
            LEDArray[i] = color
    pass