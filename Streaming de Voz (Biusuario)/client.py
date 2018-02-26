# coding=utf-8
import zmq
import sys
import os
import os.path as path
import socket
import pyaudio
import wave
import threading



CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

def Enviar(CanalSolicitudes, Receptor):

	p = pyaudio.PyAudio()


	stream = p.open(format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	frames_per_buffer=CHUNK)


	#Ciclo para grabar audio y enviarlo
	while True:

		audio = stream.read(CHUNK)

		CanalSolicitudes.send_json({"op": "Online","touser": Receptor, "audio": audio.decode('UTF-8','ignore')})
		CanalSolicitudes.recv_string()

	stream.stop_stream()
	stream.close()
	p.terminate()



def Recibir(CanalServidor, CanalMio):

	p = pyaudio.PyAudio()


	stream = p.open(format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	frames_per_buffer=CHUNK)

	while True:

		solicitud = CanalMio.recv_json()

		if solicitud["op"]=="Llamando":
			print("El usuario {} te está llamando".format(solicitud["solicitud"]))
			print("Llamando->Online")
			CanalMio.send_string("Listo")

		elif solicitud["op"] ==  "Estableciendo":

			#Hilo para enviar info al servidor
			threading.Thread(target= Enviar, args=(CanalServidor, solicitud["receptor"])).start()
			CanalMio.send_string("Listo")


		elif solicitud["op"] == "Online":
			stream.write(solicitud["audio"].encode('UTF-8','ignore'))
			CanalMio.send_string("Listo")

		else:
			CanalMio.send_string("Listo")
					

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


	if eleccion=='1':
		com=input("Digite el nombre del usuario con el cual desea conectarse: ")
		sc.send_json({"op":"Llamar","nombreenv": name})
		sc.recv_json()
		sc.send_json(com)

	#Socket para escuchar
	canal= context.socket(zmq.REP)
	canal.bind("tcp://*:{}".format(puerto))


	threading.Thread(target = Recibir, args = (sc, canal)).start()



if __name__=='__main__':
    main()