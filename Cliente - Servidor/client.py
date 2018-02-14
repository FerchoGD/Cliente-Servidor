import zmq
import sys
import time
import os
import os.path as path

def main():
    if len(sys.argv)!=4:
        print ("Error!!!")
        exit()
    ip = sys.argv[1] #Server's ip
    port = sys.argv[2] #Server's port
    operation = sys.argv[3] #Operation to perform

    context= zmq.Context()
    s = context.socket(zmq.REQ)
    s.connect("tcp://{}:{}".format(ip,port))


    if operation=="list":
        s.send_json({"op":"list"})
        files = s.recv_json()
        print(files)

    elif operation=="download":
        name=input("file to download?")
        s.send_json({"op":"download","file": name})


        numberofparts = int(s.recv_json())
        s.send_json("Hi")

        i=1
        op="si"


        if path.exists(name):

            print("El archivo ya existe en el directorio desea sobre sobre-escribirlo ")
            op=input("[si-no]")
            if op=="no":
                exit()
            if op=="si":
                os.remove(name)

        start= int(time.time())
        while numberofparts >= i:
            file= s.recv()
            with open(name,"ab+") as output:
                output.write(file)
                parte=('Parte',i)
                s.send_json(parte)
                i=i+1
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
