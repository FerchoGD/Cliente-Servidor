import zmq
import sys
import time
import os
import os.path as path
import pyaudio
import wav
import pygame

def main():
    if len(sys.argv)!=5:
        print ("Error!!!")
        exit()
    ip = sys.argv[1] #Server's ip
    port = sys.argv[2] #Server's port
    operation = sys.argv[3] #Operation to perform
    user =  sys.argv[4]

    context= zmq.Context()
    s = context.socket(zmq.REQ)
    s.connect("tcp://{}:{}".format(ip,port))

    if operation=="Send":
        usertosend=input("¿Username to send?")

        s.send_json({"msg": usertosend})

        inicio=input("Please press ENTER for record the audio \n For Finish press ENTER.")
        start= int(time.time())

        


        """ Record a few seconds of audio and save to a WAVE file. """

        chunk = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        WAVE_OUTPUT_FILENAME = "audio.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        input = True,
                        frames_per_buffer = chunk)

        print "Recording..."
        all = []
        

        #Esperando la tecla enter para finalizar
        while K_KP_ENTER != event.key:
            data = stream.read(chunk)
            all.append(data)
        print "finish recording"

        stream.close()
        p.terminate()

        # write data to WAVE file
        data = ''.join(all)
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()

        #Ciclo para mandar el archivo al servidor por partes


        with open(WAVE_OUTPUT_FILENAME, "rb") as input:
            datos=input.read()
            tam=input.tell()
            lim=tam/(1024*1024)
            print("Tamaño: "+ str(tam))
            parts=int(lim+1)
            i=0
            print ("Partes: "+ str(parts))
            
            input.seek(0)
            envia=s.recv_json()
            while i<=lim:
                data2=input.read(1024*1024)
                result=open("Parte"+str(i+1)+".mp3","ab+")
                result.write(data2)
                s.send(data2) 
                op=s.recv_json()
                print("Envio "+ op)
                i+=1


        final=input("Sending...")

    elif operation=="Listen":
        

        
    print("successful operation")

    finish= int(time.time())

    tiempo = int(finish - start)

    print (tiempo)
    exit()



    else:
        print("Error!! Unsupported operation")

    print("Connecting to server {} at {}".format(ip,port))

if __name__=='__main__':
    main()
