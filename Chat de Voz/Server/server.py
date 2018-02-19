
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
	al=s.bind("tcp://*:{}".format(port))

	print (al)

	'''Usuarios={"albert": canal}
	
	if "albert" in Usuarios:
		"enviar"
	else:
		Usuarios["albert"] = canal'''


	while True:
		msg= s.recv_json()
		for user in Usuarios:
			if msg[usertosend]==user[0]:
				with open("Para "+usertosend+".wav", "wb") as input:
					

					data=input.read()
					tam=input.tell()
					lim=tam/(1024*1024)
					print("Tamaño: "+ str(tam))
					parts=int(lim+1)
					i=0
					print ("Partes: "+ str(parts))
					s.send_json(parts)
					input.seek(0)
					envia=s.recv_json()
					while i<=lim:
						data2=input.read(1024*1024)
						result=open("Parte"+str(i+1)+".mp3","ab+")
						result.write(data2)
						s.send(data2) 
						op=s.recv_json()
						print("Enviada: "+ op[0] + str(op[1]))
						i+=1
					break
					

			else:
				print("Unsupported action")
	exit()

if __name__=='__main__':
    main()
