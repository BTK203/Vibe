#
# CONSTANT METRONOME FOR PRISM VIBE PROJECT
# Written By: Brach Knutson
#
# This program emits a constant beat with no regard to the outside environment
# Should be used as a backup should AdaptiveMetronome.py is not reliable
# enough for performance.
#

import time
import Util
import Emitter
import Constants

#constants
BEAT_FREQUENCY = Constants.INITIAL_BEAT #in Beats Per Minute. EDIT IN CONSTANTS!

#vars
beatSPB = 0 #beat frequency but in Seconds Per Beat
lastBeatTime = 0

def stream():
    print("Running")
    while True:
        global lastBeatTime
        currentTime = time.time()
        timeSinceLastBeat = currentTime - lastBeatTime
        if timeSinceLastBeat >= beatSPB: #we due for a beat
            Emitter.beat(BEAT_FREQUENCY)
            lastBeatTime = currentTime

#Program starts here
if __name__ == "__main__":
    try:
        print("Initializing")
        Emitter.init()
        beatSPB = Util.toSecondsPerBeat(BEAT_FREQUENCY)
        lastBeatTime = time.time()
        stream()
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected!")
    finally:
        Emitter.kill()