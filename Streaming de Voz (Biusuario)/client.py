# coding=utf-8
import zmq
import sys
import time
import os
import os.path as path
import socket
from random import randrange
import pyaudio
import wave
import json


def Enviar(CanalServidor):

	p = pyaudio.PyAudio()


	stream = audio.open(format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	frames_per_buffer=CHUNK)


	#Ciclo para grabar audio y enviarlo
	while True:

		audio = stream.read(CHUNK)

		CanalServidor.send_json(audio.decode('UTF-8','ignore'))
		CanalServidor.recv_json()

	stream.stop_stream()
	stream.close()
	p.terminate()



def Recibir(CanalServidor, CanalMio):

	p = pyaudio.PyAudio()


	stream = audio.open(format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	frames_per_buffer=CHUNK)

	while True:
		recibir = CanalMio.recv_json()
		stream.write(recibir.decode('UTF-8','ignore'))
		threading.Thread(target= Enviar, args=(CanalServidor)).start()

	stream.stop_stream()
	stream.close()
	p.terminate()

def main():


	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100

	get_myip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	get_myip.connect(("gmail.com",80))
	Myip = get_myip.getsockname()


    ip = sys.argv[1] #Server's ip
    port = sys.argv[2] #Server's port


    if len(sys.argv)!=3:
        print ("Error!!!")
        exit()

    

    context= zmq.Context() #Contexto para los sockets

    #Conexión con el servidor
    sc = context.socket(zmq.REQ)
    sc.connect("tcp://{}:{}".format(ip,port))

    #Nombre de usuario que se está conectando
    name=input("Tu Nombre: ")
    sc.send_json({"op":"Registrarse","nombreenv": name,"ip":Myip})
    puerto = sc.recv_json()

    eleccion = input("¿Desea realizar una llamada? \n 1.Si\n 2.No")


    if eleccion==1:
    	com=input("Digite el nombre del usuario con el cual desea conectarse:")
    	sc.send_json({"op":"Llamar","nombreenv": name,"ip":Myip})
    	sc.recv_json()
    	sc.send_json(com)

    #Socket para escuchar
    canal= context.socket(zmq.REP)
    canal.bind("tcp://* :{}".format(puerto))

    
    threading.Thread(target = Recibir, args = (sc, canal, name)).start()



if __name__=='__main__':
    main()