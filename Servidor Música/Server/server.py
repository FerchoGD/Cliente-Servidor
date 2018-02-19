import zmq
import time
import sys
import os


def LoadFiles(path):
    files={}
    dataDir=os.fsencode(path)
    for file in os.listdir(dataDir):
        filename = os.fsdecode(file)
        print("Loading {}".format(filename))
        files[filename] = file
    return files

def main():
	if len(sys.argv) != 3:
		print ("Error")
		exit()

	directory = sys.argv[2]
	port = sys.argv[1]

	context = zmq.Context()
	s = context.socket(zmq.REP)
	s.bind("tcp://*:{}".format(port))

	files = LoadFiles(directory)

	while True:
		msg= s.recv_json()
		if msg["op"]=="list":
			s.send_json({"files": list(files.keys())})
		elif msg["op"]=="download":
			filename = msg["file"]
			if filename in files:
				with open(directory + filename, "rb") as input:
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
