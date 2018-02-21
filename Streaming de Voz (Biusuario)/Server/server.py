import zmq
import time
import sys
import os

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
		if msg["op"]=="Registrar":
			peta+=1
			listausuarios.append({"nombre": msg["nombreenv"], "ip": msg["ip"],"port":peta})
			for usuario in listausuarios:
				print (usuario["nombre"])
			s.send_json(peta)
		elif msg["op"]=="Enviar":
			print("")

if __name__=='__main__':
    main()
