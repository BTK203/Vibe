#
# METRONOME PROGRAM FOR PRISM VIBE MACHINE
# Written By: Brach Knutson
# 
# This program uses input from an audio stream to derive a beat,
# which will be sent every beat to a remote or local program via
# socket. In the case of the vibe machine, signal from this program
# will be used to sync LEDs to music being played.
#

import pyaudio
import numpy
import numpy.fft as FFT
import struct
import time
import Util
import Emitter
import Constants

#metronome constants
SPECTRUM_TO_ANALYZE = 0
INITIAL_BALLPARK_BEAT = Constants.INITIAL_BEAT #approximate beat in beats per minute. EDIT IN CONSTANTS!
BEAT_SAMPLE_RANGE = 6 #number of bass values to analyze to derive a beat
BEAT_SAMPLE_AVERAGE = 3 #minimum sample volume to be considered for beat
BEAT_INCREMENT_SENSITIVITY = 1
BEAT_ALLOWABLE_ERROR = (1/8) #flexibility of beat time in beats. For example, if set to (1/32), beat will be accepted if it happens within 1/32 of the predicted beat (1/32 is VERY sensitive)
MAX_BEAT_SAMPLES = 5

#audio constants
AUDIO_FORMAT = pyaudio.paInt16
AUDIO_RATE = 44100
AUDIO_CHANNELS = 1
AUDIO_DEVICE = 1
AUDIO_CHUNK_SIZE = 1024

#FFT constants
FFT_DESIRED_SIZE = 8
FFT_EDGE_CHOP = 1 #FFT_EDGE_CHOP is the number of slices to remove from each end of the finalized FFT (to remove outliers)
FFT_NOISE_SUPPRESSION = 4
FFT_SCALE = 4
PRINT_FFT = False

#metronome variables
bassSamples = []
beatSamples = []
lastBeatTime = -1
currentBPM = INITIAL_BALLPARK_BEAT

#audio variables
audiodriver = 0
audiostream = 0

def initializeAudioStream():
    """
    Initializes the audio stream into the global variables audiodriver and audiostream.
    """

    global audiodriver
    global audiostream
    audiodriver = pyaudio.PyAudio()
    audiostream = audiodriver.open(format = AUDIO_FORMAT, rate = AUDIO_RATE, \
                            channels = AUDIO_CHANNELS, input_device_index = AUDIO_DEVICE, \
                            input = True, frames_per_buffer = AUDIO_CHUNK_SIZE)

def killAudioStream():
    """
    Shuts down the audio stream and audio driver.
    """

    audiostream.stop_stream()
    audiostream.close()
    audiodriver.terminate()

def initializeSocket():
    Emitter.init()

def killSocket():
    Emitter.kill()

def getFFT(data):
    """
    Gets the FFT of data and returns it.
    :param data: A numpy array containing raw audio data.
    """

    rawTransform = FFT.fft(data)
    trimmedTransform = rawTransform[:len(rawTransform) // 10] # select range of data we want (first tenth)
    trimmedTransform = numpy.abs(trimmedTransform) / 1000 #get rid of complex nums and reduce magnitudes

    #split the transform into slices and sum all of them
    currentSize = len(trimmedTransform)
    sizeBeforeRemoval = FFT_DESIRED_SIZE + (FFT_EDGE_CHOP * 2)
    interval = currentSize // sizeBeforeRemoval

    processedWithOutliers = []
    for i in range(0, sizeBeforeRemoval - 1):
        section = sum(trimmedTransform[i * interval : (i + 1) * interval])
        processedWithOutliers.append(section)

    #remove outliers
    processedWithoutOutliers = processedWithOutliers[FFT_EDGE_CHOP : (len(processedWithOutliers) - 1) - FFT_EDGE_CHOP]

    #clean up data a little bit
    processedWithoutOutliers = numpy.log(processedWithoutOutliers) - FFT_NOISE_SUPPRESSION
    processedWithoutOutliers *= FFT_SCALE

    return processedWithoutOutliers


def isBeat(samples, readTime):
    """
    Determines whether or not a beat has happened using samples of previous bass readings, as well as the time the potential beat was discovered.
    """
    #analyze samples for beat. In order to be considered a beat, samples must be increasing, and average of increments must be above BEAT_INCREMENT_SENSITIVITY
    sampleIncrements = Util.findIncrements(bassSamples)
    incrementAverage = Util.average(sampleIncrements)
    sampleAverage = Util.average(samples)
    if incrementAverage > BEAT_INCREMENT_SENSITIVITY and sampleAverage > BEAT_SAMPLE_AVERAGE: #thats a beat bruv
        #okay but is it supposed to be a beat though? Look at time to find out
        if lastBeatTime == -1: return True #No previous beat, making this the first.

        beatTimeValue = (readTime - lastBeatTime) / Util.toSecondsPerBeat(currentBPM) #The correlation of the timing of the beat in question compared to that of the average beat. 1 is perfect.
        beatError = abs(1 - beatTimeValue) % 1
        return beatError <= BEAT_ALLOWABLE_ERROR
    
    return False


def stream():
    global bassSamples
    global lastBeatTime
    global currentBPM
    """
    The main method. Loops infinitely, streaming audio and processing it into a beat.
    """
    
    print("Running")
    while True:
        audiodata = audiostream.read(AUDIO_CHUNK_SIZE)
        audioformat = "%dH" % (len(audiodata) / 2)
        rawdata = struct.unpack(audioformat, audiodata)
        rawdata = numpy.array(rawdata, dtype='h')

        fft = getFFT(rawdata) #fft is array

        #isolate bass
        bass = fft[SPECTRUM_TO_ANALYZE]
        bassSamples.append(bass)

        if PRINT_FFT:
            Util.displayArrayAsGraph(fft)

        #limit size of sample array to BEAT_SAMPLE_RANGE
        while len(bassSamples) > BEAT_SAMPLE_RANGE:
            bassSamples.pop(0)
        
        timeOfReading = time.time()
        if isBeat(bassSamples, timeOfReading):
            #record beat: add beat to beat samples, set last beat time, calculate new average BPM
            instantaneousBPM = Util.toBeatsPerMinute(timeOfReading - lastBeatTime) if (lastBeatTime > 0) else INITIAL_BALLPARK_BEAT
            
            #ensure instantaneousBPM is within beat allowable error to avoid outliers
            approximateMultiple = Util.roundWhole(currentBPM / instantaneousBPM)
            instantaneousBPM *= approximateMultiple

            beatSamples.append(instantaneousBPM)
            while len(beatSamples) > MAX_BEAT_SAMPLES: #regulate size of sample beats to MAX_BEAT_SAMPLES
                beatSamples.pop(0)

            #set lastBeatTime
            lastBeatTime = timeOfReading

            #figure out new average BPM
            currentBPM = Util.average(beatSamples)

            Emitter.beat(currentBPM)


#program starts here
if __name__ == "__main__":
    try:
        print("Initializing")
        initializeAudioStream()
        initializeSocket()
        beatSamples = Util.filledArray(INITIAL_BALLPARK_BEAT, MAX_BEAT_SAMPLES)
        print("Initialization complete.")

        #do other stuff here
        stream()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected!")
    finally:
        print("Stopping")
        killAudioStream()
        killSocket()
        print("Stopped.")