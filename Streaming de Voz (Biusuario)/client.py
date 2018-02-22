# coding=utf-8
import zmq
import sys
import time
import os
import os.path as path
import socket
from random import randrange
import pip
#import pyaudio
import wave

def main():
    sip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    sip.connect(("gmail.com",80)) 
    ipuse=sip.getsockname()
    ip=ipuse[0]
    print(ip)

    if len(sys.argv)!=3:
        print ("Error!!!")
        exit()

    ip = sys.argv[1] #Server's ip
    port = sys.argv[2] #Server's port

    context= zmq.Context() #Contexto para los sockets

    sc = context.socket(zmq.REQ)
    sc.connect("tcp://{}:{}".format(ip,port))
    #Nobre de usuario que se está conectando
    name=input("Nombre")
    sc.send_json({"op":"Conectarse","nombreenv": name,"ip":ip})
    puerto = sc.recv_json()

    com=input("Digite el nombre del usuario con el cual desea conectarse")
    sc.send_json(com)


    canal= context.socket(zmq.REP)
    canal.bind("tcp://*:{}".format(puerto))

    #Ciclo para el Streaming
    while True:
          
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 0.55
        WAVE_OUTPUT_FILENAME = "voice.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* recording")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()


    pygame.quit()
        



if __name__=='__main__':
    main()