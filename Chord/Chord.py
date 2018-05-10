import hashlib
import random
import sys
import threading
import zmq
import os
import math
from time import sleep



cant_nodos = 16

pot = int(math.log2(cant_nodos))


class Nodo():

	def __init__(self,iṕ,puerto,ide):
		self.id=ide
		self.finger_table = {}
		self.sucesor = -1
		self.predecesor = -1
		self.ip = ip
		self.puerto = puerto
		self.range_x = 0
		self.range_y = 0

	def GetSucesor():
		return self.sucesor

	def GetPredecesor():
		return self.predecesor

	def GetIp():
		return self.ip

	def GetId():
		return self.id

	def GetPuerto():
		return self.puerto


	def SetSucesor(new_sucesor):
		self.sucesor = new_sucesor

	def SetPredecesor(new_predecesor):
		self.predecesor = new_predecesor

	def SetX(num_x):
		self.range_x = num_x

	def SetY(num_y):
		self.range = num_y

	def GetX():
		return range_x

	def GetY():
		return range_y

	def Finger(self):
		for i in range(0,pot):
			llave = self.GetId() + 2 ** i
			self.finger_table[llave] = {}

	def Actualizar_Finger(self,table):
		for key in self.finger_table:
			finger_table[key] = table[key]





def Server():

	




def Main():

	if(len(sys.argv) == 3):
		my_ip = sys.argv[1]
		my_port = sys.argv[2]

		ide = random.randrange(15)

		nuevo = Nodo(my_ip, my_port,ide)
		comp_x = nuevo.GetId() + 1
		comp_y = nuevo.GetId()

		nuevo.setX(comp_x)
		nuevo.SetY(comp_y)

		conectado = True

	if(len(sys.argv) == 5):
		my_ip = sys.argv[1]
		my_port = sys.argv[2]
		ide = random.randrange(15)

		nuevo = Nodo(my_ip, my_port,ide)

		other_ip = sys.argv[3]
		other_port = sys.argv[4]

		address = "tcp://"+other_ip+":"+other_port		
		conectado = False


	context= zmq.context()
	socket_cliente = context.socket(zmq.REQ)
	socket_servidor = context.socket(zmq.REP)


	while not conectado:

		socket_cliente.connect(address)

		data = {"op": "conexion","id": nuevo.GetId()}
		socket_cliente.send_json(data)
		respuesta = socket_cliente.recv_string()

		if(respuesta["op"] == "Aqui es"):


