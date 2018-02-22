import zmq
import time
import sys
import os
import threading


def main():
	if len(sys.argv) != 2:
		print ("Error")
		exit()

	port = sys.argv[1]

	context = zmq.Context()
	s = context.socket(zmq.REP)
	s.bind("tcp://*:{}".format(port))
	peta=4000

	listausuarios=[]


	while True:

		msg= s.recv_json()
		if msg["op"]=="Conectarse":
			peta+=1
			
			#Añadiendo cada usuario que se conecta a la lista
			listausuarios.append({"nombre": msg["nombreenv"], "ip": msg["ip"],"port":peta})
			'''for usuario in listausuarios:
				print (usuario["nombre"])'''

			s.send_json(peta)

			usertoconect=s.recv_json()

			if usertoconect in listausuarios["nombre"]:

				conexion = context.socket(zmq.REP)
				conexion.connect("tcp://{}:{}".format(listausuarios["ip"],listausuarios["port"]))


		else:
			print("Operación no definida!! -_-")

if __name__=='__main__':
    main()
