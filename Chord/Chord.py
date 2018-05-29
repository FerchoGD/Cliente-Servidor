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

	def __init__(self,ip,puerto,ide):
		self.id=ide
		self.finger_table = {}
		self.ip = ip
		self.puerto = puerto
		self.range_x = 0
		self.range_y = 0

	def GetSucesor(self):
		return self.sucesor

	def GetPredecesor(self):
		return self.predecesor

	def GetIp(self):
		return self.ip

	def GetId(self):
		return self.id

	def GetPuerto(self):
		return self.puerto


	def SetSucesor(new_sucesor):
		self.sucesor = new_sucesor

	def SetPredecesor(new_predecesor):
		self.predecesor = new_predecesor

	def SetX(self,num_x):
		self.range_x = num_x

	def SetY(self,num_y):
		self.range_y = num_y

	def GetX(self):
		return self.range_x

	def GetY(self):
		return self.range_y

	def GetFinger(self):
		return self.finger_table

	def Finger(self):
		for i in range(0,pot):
			llave = self.GetId() + 2 ** i
			self.finger_table[llave] = {"id" : self.GetId(), "ip": self.GetIp(), "puerto" : self.GetPuerto()}


	#Pendiente de Modificiacion
	def Actualizar_Finger(self,table):
		for key in self.finger_table:
			finger_table[key] = table[key]

#Funcion para verificar si estoy en el rango del nodo
def Verificar(id_entrada, mi_x, mi_y):
	resultado = False
	if( mi_x > mi_y):
		if(id_entrada > mi_x or id_entrada < mi_y):
			resultado = True

	else:
		if(id_entrada > mi_x and id_entrada < mi_y):
			resultado = True

	return resultado




def Server(canal_servidor, port, mi_nodo):
	canal_servidor.bind("tcp://*:"+port)

	while True:
		mensaje = canal_servidor.recv_json()

		if (mensaje["op"] == "conexion"):
			entrada_nodo_id = mensaje["id"]

			aqui_es = Verificar(entrada_nodo_id, mi_nodo.GetX(), mi_nodo.GetY())

			if(aqui_es):
				if(mi_nodo.GetId() > entrada_nodo_id):

					data={"op": "si", "x":mi_nodo.GetX() , "y":entrada_nodo_id,"server_id": mi_nodo.GetId()}
					mi_nodo.SetX(entrada_nodo_id+1)
					mi_nodo.SetY(mi_nodo.GetId())
					print(mi_nodo.GetX())
					print(mi_nodo.GetY())
					canal_servidor.send_json(data)

				else:

					data={"op": "si", "x":mi_nodo.GetY()+1, "y": entrada_nodo_id, "server_id": mi_nodo.GetId()}
					mi_nodo.SetX(entrada_nodo_id+1)
					mi_nodo.SetY(mi_nodo.GetId())
					print(mi_nodo.GetX())
					print(mi_nodo.GetY())
					canal_servidor.send_json(data)
			else:
				table = mi_nodo.GetFinger()
				minimo = 70
				id_min = 0
				ip_min = 0
				puerto_min = 0
				for llave in table:
					if(table[llave]["id"] - entrada_nodo_id < minimo):
						id_min = table[llave]["id"]
						ip_min = table[llave]["ip"]
						puerto_min = table[llave]["puerto"]
						minimo = table[llave]["id"] - entrada_nodo_id
				data={"op" : "siguiente", "id" : id_min, "ip": ip_min, "puerto": puerto_min}
				canal_servidor.send_json(data)

		elif(mensaje["op"] == "actualizando"):
			llave_check = mensaje["llave"]
			if(Verificar(llave_check, mi_nodo.GetX(), mi_nodo.GetY())):
				msj = {"op": "es_llave", "id": mi_nodo.GetId(), "ip": mi_nodo.GetIp() , "puerto": mi_nodo.GetPuerto()}
			else:
				my_finger = mi_nodo.GetFinger()
				minimo = 70
				for key in  my_finger:
					if( my_finger[key]["id"] - llave_check < minimo):
						minimo = my_finger[key]["id"] - llave_check
						sgte_id = my_finger[key]["id"]
						sgte_ip = my_finger[key]["ip"]
						sgte_port = my_finger[key]["puerto"]
				msj = {"op": "no_es_llave", "id": sgte_id, "ip": sgte_ip , "puerto": sgte_port}
			canal_servidor.send_json(msj)

		elif(mensaje["op"] == "rueda_la_bola"):
			if(mensaje["start"] != mi_nodo.GetId()):
				#Actualizando Finger
				finger = mi_nodo.GetFinger()
				
				for key in finger:
					if(Verificar(key, mensaje["x"], mensaje["y"])):
						finger[key]["id"] = mensaje["id"]
						finger[key]["ip"] = mensaje["ip"]
						finger[key]["puerto"] = mensaje["puerto"]
				canal_servidor.send_string("Listo")

				socket_sucesor = context.socket(zmq.REQ)
				key_sucesor = mi_nodo.GetId() + 2**0 % cant_nodos
				ip_sucesor = finger[key_sucesor]["ip"]
				puerto_sucesor = finger[key_sucesor]["puerto"]
				dir_sucesor = "tcp://"+ip_sucesor+":"+puerto_sucesor
				solicitud = {"op": "rueda_la_bola" , "id": mi_nodo.GetId(), "x": mi_nodo.GetX(), "y": mi_nodo.GetY(), "ip": mi_nodo.GetIp(), "puerto": mi_nodo.GetPuerto(), "start": mensaje["start"]}
				socket_sucesor.connect(dir_sucesor)
				socket_sucesor.send_json(solicitud)
			else:
				canal_servidor.send_string("termino_actualizar")



def main():
	if(len(sys.argv) == 3):
		my_ip = sys.argv[1]
		my_port = sys.argv[2]

		ide = random.randrange(0,cant_nodos-1)
		print(ide)
		print("\n")

		nuevo = Nodo(my_ip, my_port,ide)
		comp_x = ide + 1
		comp_y = ide

		nuevo.SetX(comp_x)
		nuevo.SetY(comp_y)
		nuevo.Finger()

		conectado = True

	if(len(sys.argv) == 5):
		my_ip = sys.argv[1]
		my_port = sys.argv[2]
		ide = random.randrange(0,cant_nodos-1)
		print(ide)
		print("\n")

		nuevo = Nodo(my_ip, my_port,ide)
		nuevo.Finger()

		other_ip = sys.argv[3]
		other_port = sys.argv[4]

		address = "tcp://"+other_ip+":"+other_port
		conectado = False


	context= zmq.Context()
	socket_cliente = context.socket(zmq.REQ)
	socket_servidor = context.socket(zmq.REP)
	thread_server = threading.Thread(target=Server, args=(socket_servidor, my_port, nuevo))
	thread_server.start()

	#Ciclo para conectar nodo
	while not conectado:

		socket_cliente.connect(address)

		data = {"op" : "conexion","id" : nuevo.GetId(), "ip" : nuevo.GetIp(), "port" : nuevo.GetPuerto()}
		socket_cliente.send_json(data)
		respuesta = socket_cliente.recv_json()

		if(respuesta["op"] == "si"):
			print(respuesta["op"])
			nuevo.SetX(respuesta["x"])
			nuevo.SetY(respuesta["y"])
			print(nuevo.GetX())
			print(nuevo.GetY())

			#Actualizando Finger
			new_finger = {}
			
			for i in range(0,pot):
				encontrado = False
				llave = (nuevo.GetId() + 2 ** i) % cant_nodos
				while not encontrado:
					socket_cliente.send_json({"op": "actualizando", "llave": llave})
					mensaje = socket_cliente.recv_json()
					if (mensaje["op"] == "es_llave"):
						new_finger[llave] = {"id" : mensaje["id"], "ip": mensaje["ip"] , "puerto" : mensaje["puerto"]}
						encontrado=True
					elif (mensaje["op"] == "no_es_llave"):
						sgte_ip = mensaje["ip"]
						sgte_port = mensaje["puerto"]
						socket_cliente.disconnect(address)
						address = "tcp://"+sgte_ip+":"+sgte_port
						socket_cliente.connect(address)
			nuevo.Actualizar_Finger(new_finger)
			print("Actualizado con exito")
			conectado=True

		elif(respuesta["op"] == "siguiente"):
			sgte_id =  respuesta["id"]
			sgte_ip = respuesta["ip"]
			sgte_port = respuesta["puerto"]
			socket_cliente.disconnect(address)
			address = "tcp://"+sgte_ip+":"+sgte_port

	


		sucesor_finger = nuevo.GetFinger()
		key_sucesor = nuevo.GetId() + 2 ** 0
		sucesor={"id": sucesor_finger[key_sucesor]["id"], "ip": sucesor_finger[key_sucesor]["ip"], "puerto": sucesor_finger[key_sucesor]["puerto"]}
		solicitud = {"op": "rueda_la_bola" , "id": nuevo.GetId(), "x": nuevo.GetX(), "y": nuevo.GetY(), "ip": nuevo.GetIp(), "puerto": nuevo.GetPuerto(), "start": nuevo.GetId()}

		socket_cliente.disconnect(address)
		address = "tcp://"+sucesor["ip"]+":"+sucesor["puerto"]
		socket_cliente.connect(address)
		socket_cliente.send_json(solicitud)
		socket_cliente.recv_string()


main()