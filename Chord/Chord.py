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

	def GetIp(self):
		return self.ip

	def GetId(self):
		return self.id

	def GetPuerto(self):
		return self.puerto


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
			llave = (self.id + 2 ** i) % cant_nodos
			self.finger_table[llave] = {"id" : self.id, "ip": self.ip, "puerto" : self.puerto}


	#Recibiendo y actualizando con una nueva finger
	def Actualizar_Finger(self,table):
		for key in self.finger_table:
			#print("Llave: "+str(key)+" "+str(self.finger_table[key]))
			#print(table[key])
			self.finger_table[key] = table[key]


	#Imprimir finger

	def Mostrar_Finger(self):
		for key in self.finger_table:
			print(str(key) +" "+str(self.finger_table[key]))
			#print(self.finger_table[key])
			
#Funcion para verificar si estoy en el rango del nodo
def Verificar(id_entrada, mi_x, mi_y):
	resultado = False
	if( mi_x > mi_y):
		if(id_entrada >= mi_x or id_entrada <= mi_y):
			resultado = True

	else:
		if(id_entrada >= mi_x and id_entrada <= mi_y):
			resultado = True

	return resultado




def Server(canal_servidor, port, mi_nodo,contexto):
	canal_servidor.bind("tcp://*:"+port)

	while True:
		mensaje = canal_servidor.recv_json()

		if (mensaje["op"] == "conexion"):
			print("\n")
			print("Se estan conectado a mi"+"\n")
			entrada_nodo_id = mensaje["id"]

			aqui_es = Verificar(entrada_nodo_id, mi_nodo.GetX(), mi_nodo.GetY())

			if(aqui_es):
				if(mi_nodo.GetId() > entrada_nodo_id):

					data={"op": "si", "x":mi_nodo.GetX() , "y":entrada_nodo_id}
					mi_nodo.SetX(entrada_nodo_id+1)
					mi_nodo.SetY(mi_nodo.GetId())
					print("Rango: "+str(mi_nodo.GetX()) +" - "+ str(mi_nodo.GetY()))
					

				else:

					data={"op": "si", "x":mi_nodo.GetY()+1, "y": entrada_nodo_id}
					mi_nodo.SetX(entrada_nodo_id+1)
					mi_nodo.SetY(mi_nodo.GetId())
					print("Rango: "+str(mi_nodo.GetX()) +" - "+ str(mi_nodo.GetY())+"\n")
			else:
				table = mi_nodo.GetFinger()
				Stop = True
				
				for llave in table:
					if(table[llave]["id"] > entrada_nodo_id):
						if(Stop):
							id_Sig = table[llave]["id"]
							ip_Sig = table[llave]["ip"]
							puerto_Sig = table[llave]["puerto"]
							Stop=False

				data={"op" : "siguiente", "id" : id_Sig, "ip": ip_Sig, "puerto": puerto_Sig}
			canal_servidor.send_json(data)	

		elif(mensaje["op"] == "actualizando"):
			print("Actualizando Inicio  --- Actualizando finger del nuevo")
			#mi_nodo.Mostrar_Finger()
			llave_check = mensaje["llave"]

			print(llave_check)
			if(Verificar(llave_check, mi_nodo.GetX(), mi_nodo.GetY())):
				msj = {"op": "es_llave", "id": mi_nodo.GetId(), "ip": mi_nodo.GetIp() , "puerto": mi_nodo.GetPuerto()}
			else:
				my_finger = mi_nodo.GetFinger()
				Stop = True
				for key in  my_finger:
					if( my_finger[key]["id"] >= llave_check):
						if(Stop):
							sgte_id = my_finger[key]["id"]
							sgte_ip = my_finger[key]["ip"]
							sgte_port = my_finger[key]["puerto"]
							Stop=False
					banderaKeyFinal=key
				if(Stop):
					print("No estoy ")
					sgte_id = my_finger[banderaKeyFinal]["id"]
					sgte_ip = my_finger[banderaKeyFinal]["ip"]
					sgte_port = my_finger[banderaKeyFinal]["puerto"]
					print(str(sgte_id)+"  "+str(sgte_ip)+" "+str(sgte_port))



				msj = {"op": "no_es_llave", "id": sgte_id, "ip": sgte_ip , "puerto": sgte_port}
			canal_servidor.send_json(msj)
			print("Actualizando Fin")


		elif(mensaje["op"] == "rueda_la_bola"):
			
			print("-------------------------------------------------")
			#Actualizando Finger
			finger = mi_nodo.GetFinger()
			
			for key in finger:
				if(Verificar(key, mensaje["x"], mensaje["y"])):
					finger[key]["id"] = mensaje["id"]
					finger[key]["ip"] = mensaje["ip"]
					finger[key]["puerto"] = mensaje["puerto"]
			canal_servidor.send_string("Listo")
			print("RODANDO LA BOLA")
			mi_nodo.Actualizar_Finger(finger)
			mi_nodo.Mostrar_Finger()			

			if(mensaje["start"] != finger[(mi_nodo.GetId() + 2 ** 0) % cant_nodos]["id"]):
				socket_sucesor = contexto.socket(zmq.REQ)
				key_sucesor = (mi_nodo.GetId() + 2**0) % cant_nodos
				ip_sucesor = finger[key_sucesor]["ip"]
				puerto_sucesor = finger[key_sucesor]["puerto"]
				dir_sucesor = "tcp://"+ip_sucesor+":"+puerto_sucesor
				solicitud = {"op": "rueda_la_bola" , "id": mensaje["id"], "x": mensaje["x"], "y": mensaje["y"], "ip": mensaje["ip"], "puerto": mensaje["puerto"], "start": mensaje["start"]}
				socket_sucesor.connect(dir_sucesor)
				socket_sucesor.send_json(solicitud)
				socket_sucesor.disconnect(dir_sucesor)
			




def main():
	if(len(sys.argv) == 3):
		my_ip = sys.argv[1]
		my_port = sys.argv[2]

		#ide = random.randrange(0,cant_nodos-1)
		ide=int(input("Id : "))
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
		#ide = random.randrange(0,cant_nodos-1)
		ide=int(input("Id : "))

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
	thread_server = threading.Thread(target=Server, args=(socket_servidor, my_port, nuevo, context))
	thread_server.start()

	#Ciclo para conectar nodo
	
	while not conectado:

		socket_cliente.connect(address)

		data = {"op" : "conexion","id" : nuevo.GetId(), "ip" : nuevo.GetIp(), "puerto" : nuevo.GetPuerto()}
		socket_cliente.send_json(data)
		respuesta = socket_cliente.recv_json()

		if(respuesta["op"] == "si"):
			print(respuesta["op"])
			nuevo.SetX(respuesta["x"])
			nuevo.SetY(respuesta["y"])
			print("Rango: "+str(nuevo.GetX()) +" - "+ str(nuevo.GetY())+"\n"+"\n")

			

			#Actualizando Finger
			new_finger = {}
			for i in range(0,pot):
				encontrado = False
				llave = (nuevo.GetId() + 2 ** i) % cant_nodos
				print(llave)
				
				if(Verificar(llave,nuevo.GetX(),nuevo.GetY())):
					new_finger[llave] = {"id" : nuevo.GetId(), "ip": nuevo.GetIp() , "puerto" : nuevo.GetPuerto()}
					print("Me pertenece esta llave")
				else:
					while not encontrado:
						socket_cliente.send_json({"op": "actualizando", "llave": llave})
						#print(llave)
						mensaje = socket_cliente.recv_json()
						#print(mensaje)
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
			print("\n")
			print("He Actualizado mi finger con exito"+"\n")
			nuevo.Mostrar_Finger()
			conectado=True

		elif(respuesta["op"] == "siguiente"):
			sgte_id =  respuesta["id"]
			sgte_ip = respuesta["ip"]
			sgte_port = respuesta["puerto"]
			socket_cliente.disconnect(address)
			address = "tcp://"+sgte_ip+":"+sgte_port


	

		if(conectado):
			sucesor_finger = nuevo.GetFinger()
			key_sucesor = (nuevo.GetId() + 2 ** 0) % cant_nodos
			sucesor={"id": sucesor_finger[key_sucesor]["id"], "ip": sucesor_finger[key_sucesor]["ip"], "puerto": sucesor_finger[key_sucesor]["puerto"]}
			solicitud = {"op": "rueda_la_bola" , "id": nuevo.GetId(), "x": nuevo.GetX(), "y": nuevo.GetY(), "ip": nuevo.GetIp(), "puerto": nuevo.GetPuerto(), "start": nuevo.GetId()}

			socket_cliente.disconnect(address)
			address = "tcp://"+sucesor["ip"]+":"+sucesor["puerto"]
			socket_cliente.connect(address)
			socket_cliente.send_json(solicitud)
			socket_cliente.recv_string()


main()
