# coding=utf-8
import zmq
import sys
import os
import os.path as path
import socket
import pyaudio
import wave
import threading
import time
#variables
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100



def Recibir(CanalServidor, CanalMio):

	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					output=True,
					frames_per_buffer=CHUNK
					)
	while True:

		solicitud = CanalMio.recv_json()
		if solicitud["op"] ==  "Estableciendo":
			#Hilo para enviar info al servidor
			CanalMio.send_json("Listo")
			threading.Thread(target= Enviar, args=(CanalServidor, solicitud["receptor"])).start()
			
		elif solicitud["op"] == "Online":

			print("escucho")
			stream.write(solicitud["audio"].encode('UTF-16','ignore'))
			CanalMio.send_string("Listo")
					
	stream.stop_stream()
	stream.close()
	p.terminate()

def Enviar(CanalServidor, Receptor):

	p = pyaudio.PyAudio()


	stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK	
					)

	#Ciclo para grabar audio y enviarlo
	while True:

		audio = stream.read(CHUNK)
		print("hablo")
		CanalServidor.send_json({"op": "Online","touser": Receptor, "audio": audio.decode('UTF-16','ignore')})
		CanalServidor.recv_json()

	stream.stop_stream()
	stream.close()
	p.terminate()



def main():

	#Obteniendo mi ip
	get_myip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	get_myip.connect(("gmail.com",80))
	Myip , basura = get_myip.getsockname()
	print(Myip)

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

	eleccion = input("¿Desea realizar una llamada? \n 1.Si\n 2.No \n Tu Respuesta>> ")
	

	if eleccion == '1':
		eleccion2 = input("\n \n ¿Con quien desea conectarse? \n 1.Persona especifica\n 2.Grupo conectado al servidor \n Tu Respuesta>> ")
		if eleccion2=='1':
			com=input("Digite el nombre del usuario con el cual desea conectarse: ")
			sc.send_json({"op":"Llamar","nombreenv": name})
			sc.recv_json()
			sc.send_json(com)
			sc.recv_json()
		if eleccion2 == '2':
			sc.send_json({"op":"LlamarGrupo","nombreenv": name})
			sc.recv_json()
 
	#Socket para escuchar
	canal= context.socket(zmq.REP)
	canal.bind("tcp://*:{}".format(puerto))


	threading.Thread(target = Recibir, args = (sc, canal)).start()



if __name__=='__main__':
    main()