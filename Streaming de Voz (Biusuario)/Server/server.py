import zmq
import time
import sys
import os
import threading
import json


def main():
	if len(sys.argv) != 2:
		print ("Error")
		exit()

	port = sys.argv[1]

	context = zmq.Context()
	s = context.socket(zmq.REP)
	s.bind("tcp://*:{}".format(port))

	#Asignando puerto
	peta=4000

	listausuarios={}


	while True:

		msg= s.recv_json()

		if msg["op"]=="Registrarse":
			peta+=1
			
			#Añadiendo cada usuario que se conecta al diccionario
			usuarionuevo = context.socket(zmq.REQ)
			usuarionuevo.connect("tcp://{}:{}".format(msg["ip"], peta))
			listausuarios[msg["nombreenv"]] = usuarionuevo
			

			s.send_json(peta)


		elif msg["op"]=="Llamar":

			s.send_json("Listo")
			usertoconect=s.recv_json()

			if listausuarios.get(usertoconect)!= None:				

				receptor = listausuarios[usertoconect]
				receptor.send_json({"op":"Llamar", "solicitud": msg["nombreenv"]})

				receptor.recv_json()

				emisor = listausuarios[msg["nombreenv"]]
				emisor.send_json({"op": "confirm", "receptor": usertoconect})
				emisor.recv_json()

				receptor.send_json({"op":"confirm","receptor": msg["nombreenv"]})
				receptor.recv_json()

				while True:
					s.send_string("Listo")
					receptor = listausuarios[usertoconect]
					receptor.send_json(msg)
					receptor.recv_string()
			else:
				print("Usuario no conectado")


		else:
			print("Operación no definida!! -_-")

if __name__=='__main__':
    main()
