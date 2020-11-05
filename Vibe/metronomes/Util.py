#
# UTILITY CLASS FOR METRONOME PROGRAM
# Written By: Brach Knutson
#
# This file contains several helpful methods for the program.
# Some methods will be used in runtime, others only while debugging.
#

import math

def displayArrayAsGraph(arr):
    try:
        for i in range(0, len(arr)):
            string = ""
            if arr[i] == math.inf or arr[i] == -math.inf:
                continue

            for n in range(0, int(arr[i])):
                string += "*"
            
            print(string + "                        " + str(arr[i]))

    except ValueError as e:
        print(e.args)
        print("ValueError occured, but handled.")

    print()
    print()
    print()


def findIncrements(arr):
    """
    Returns an array containing all increments in an array, in the order in which they happen.
    """
    increments = []

    for  i in range(0, len(arr) - 1):
        increment = arr[i + 1] - arr[i]
        increments.append(increment)

    return increments

def average(arr):
    """
    Returns the average of the array.
    """
    if len(arr) == 0: return 0

    average = 0
    for num in arr:
        average += num

    average /= len(arr)

    return average

def valuesPositive(arr):
    """
    Returns True if all values in the array are positive, and False otherwise.
    """
    for num in arr:
        if num <= 0: #not positive value!
            return False

    return True

def toSecondsPerBeat(bpm):
    """
    Takes the number of beats per minute and returns the number of seconds elapsed per beat.
    """
    return 1 / (bpm * (1/60))

def toBeatsPerMinute(spb):
    """
    Takes the number of seconds per beat and returns the number of beats per minute.
    """
    return 60 * (1 / spb)

def filledArray(number, size):
    """
    Generates an array populated with "size" number of "number"
    """
    arr = []
    for i in range(0, size):
        arr.append(number)

    return arr

def roundWhole(dec):
    """
    Rounds a decimal to the nearest whole number
    """
    return int(dec + 0.5)