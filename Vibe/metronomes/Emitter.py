#
# EMITTER PROGRAM FOR PRISM VIBE
# Written By: Brach Knutson
# 
# This program is a consistent interface for "emitting" beats, otherwise known as sending
# them across the socket to the LED driver.

import socket


#constants
SOCKET_ADDRESS = "127.0.0.1"
SOCKET_BEATING_PORT = 9999

#vars
sock = 0

def init():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((SOCKET_ADDRESS, SOCKET_BEATING_PORT))

def kill():
    sock.close()

def beat(currentBeat):
    #send information on socket. Format: "BEAT:[bpm]"
    string = "BEAT:" + str(currentBeat)
    sock.sendall(string.encode())