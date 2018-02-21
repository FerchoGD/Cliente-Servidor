# coding=utf-8
import zmq
import sys
import time
import os
import os.path as path
import socket
from random import randrange
import pygame

def main():
    sip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    sip.connect(("gmail.com",80)) 
    ipuse=sip.getsockname()
    ip=ipuse[0]
    print(ip)
    pygame.init()

    if len(sys.argv)!=3:
        print ("Error!!!")
        exit()

    ip = sys.argv[1] #Server's ip
    port = sys.argv[2] #Server's port

    context= zmq.Context()
    sc = context.socket(zmq.REQ)
    sc.connect("tcp://{}:{}".format(ip,port))
    name=input("Nombre")
    sc.send_json({"op":"Registrar","nombreenv": name,"ip":ip})
    Resp = sc.recv_json()
    print(Resp)
    print("ciclo")

    while True:
        print("fgf")
        for event in pygame.event.get():
            if event.type is KEYDOWN:
                print("holaaaa")
            else:
                print("pald")   


    pygame.quit()
        



if __name__=='__main__':
    main()