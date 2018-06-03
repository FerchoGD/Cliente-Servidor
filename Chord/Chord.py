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
			self.finger_table[llave] = {"id" : self.id, "ip": self.ip, "puerto" : self.puerto, "rangollave" : {"x" :self.range_x, "y" : self.range_y}}

	#Recibiendo y actualizando con una nueva finger
	def Actualizar_Finger(self,table):
		for key in table:
			#print("Llave: "+str(key)+" "+str(self.finger_table[key]))
			#print(table[key])
			self.finger_table[key] = table[key]

	#Imprimir finger Table
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

#Funcion que permite recorrer la finger_table de un nodo y pasarnos los parametros de su sucesor ideal.
def encontrarNodo(table,entrada_nodo_id,op):
	for llave in table:
		if(Verificar(entrada_nodo_id,table[llave]["rangollave"]["x"],table[llave]["rangollave"]["y"])):
			sgte_id = table[llave]["id"]
			sgte_ip = table[llave]["ip"]
			sgte_port = table[llave]["puerto"]
			if(op==1):
				data={"op" : "siguiente", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
			else:
				data={"op" : "no_es_llave", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
			return data

		KeyFinal=llave
	#print("No estoy en la finger")
	sgte_id = table[KeyFinal]["id"]
	sgte_ip = table[KeyFinal]["ip"]
	sgte_port = table[KeyFinal]["puerto"]
	#print(str(sgte_id)+"  "+str(sgte_ip)+" "+str(sgte_port))
	if(op==1):
		data={"op" : "siguiente", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
	else:
		data={"op" : "no_es_llave", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
	return data


#Funcion que se ejecuta en el hilo que queda esperando el ingreso de un mensaje
def Server(canal_servidor, port, mi_nodo,contexto):
	canal_servidor.bind("tcp://*:"+port)

	while True:
		mensaje = canal_servidor.recv_json()
		#condicional por medio del cual el nodo entrante busca su puesto en el chord
		if (mensaje["op"] == "conexion"):
			print("\n")
			print("Se esta conectado a mi el nodo "+str(mensaje["id"]))
			entrada_nodo_id = mensaje["id"]
			aqui_es = Verificar(entrada_nodo_id, mi_nodo.GetX(), mi_nodo.GetY())
			#Si el nodo entrante esta en el rango de llaves del nodo de ingreso.
			if(aqui_es):
				data={"op": "si", "x":mi_nodo.GetX() , "y":entrada_nodo_id}
				mi_nodo.SetX((entrada_nodo_id+1) % cant_nodos)
				mi_nodo.SetY((mi_nodo.GetId())% cant_nodos)
				print("Rango: "+str(mi_nodo.GetX()) +" - "+ str(mi_nodo.GetY()))	
			else:
				print("Lo siento, te comunico con un nodo sucesor.")
				table = mi_nodo.GetFinger()
				data=encontrarNodo(table,entrada_nodo_id,1)
			canal_servidor.send_json(data)	
		#Condicional que nos permite actualizar la finger table del nodo que esta ingresando.
		elif(mensaje["op"] == "actualizando"):
			#print("Actualizando Inicio  --- Actualizando finger del nuevo")
			#mi_nodo.Mostrar_Finger()
			llave_check = mensaje["llave"]
			#print(llave_check)
			if(Verificar(llave_check, mi_nodo.GetX(), mi_nodo.GetY())):
				#print("SI estoy")
				msj = {"op": "es_llave", "id": mi_nodo.GetId(), "ip": mi_nodo.GetIp() , "puerto": mi_nodo.GetPuerto(), "rx" :mi_nodo.GetX(), "ry" : mi_nodo.GetY()}
			else:
				my_finger = mi_nodo.GetFinger()
				msj=encontrarNodo(my_finger,llave_check,2)
			canal_servidor.send_json(msj)
			#print("Actualizando Fin")
		#Condicional que ejecuta la orden de actualizacion de las finger tables.
		elif(mensaje["op"] == "rueda_la_bola"):
			
			print("-------------------------------------------------")
			#Actualizando Finger
			finger = mi_nodo.GetFinger()
			for key in finger:
				if(Verificar(key, mensaje["rx"], mensaje["ry"])):
					finger[key]["id"] = mensaje["id"]
					finger[key]["ip"] = mensaje["ip"]
					finger[key]["puerto"] = mensaje["puerto"]
					finger[key]["rangollave"]={"x": mensaje["rx"],"y":mensaje["ry"]}

				if(Verificar(key, mensaje["rxi"], mensaje["ryi"])):
					finger[key]["rangollave"]={"x": mensaje["rxi"],"y":mensaje["ryi"]}

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
				solicitud = {"op": "rueda_la_bola" , "id": mensaje["id"], "rx": mensaje["rx"], "ry": mensaje["ry"],"rxi":mensaje["rxi"], "ryi": mensaje["ryi"],"ip": mensaje["ip"], "puerto": mensaje["puerto"], "start": mensaje["start"]}
				socket_sucesor.connect(dir_sucesor)
				socket_sucesor.send_json(solicitud)
				socket_sucesor.disconnect(dir_sucesor)

		elif(mensaje["op"] == "Eliminar_nodo"):
			if(mensaje["stop"]):
				mi_nodo.SetX(mensaje["rxi"])
			print("Rango: "+str(mi_nodo.GetX()) +" - "+ str(mi_nodo.GetY()))
			finger = mi_nodo.GetFinger()
			for key in finger:
				if(Verificar(key, mensaje["rxi"], mensaje["ryi"])):
					finger[key]["id"] = mensaje["id"]
					finger[key]["ip"] = mensaje["ip"]
					finger[key]["puerto"] = mensaje["puerto"]
					finger[key]["rangollave"]={"x": mensaje["rxi"],"y":mensaje["ryi"]}

				if(Verificar(key, mensaje["rxi"], mensaje["ryi"])):
					finger[key]["rangollave"]={"x": mensaje["rxi"],"y":mensaje["ryi"]}

			canal_servidor.send_string("Listo")
			print("Eliminar_nodo")
			mi_nodo.Actualizar_Finger(finger)
			mi_nodo.Mostrar_Finger()	
			socket_sucesor = contexto.socket(zmq.REQ)
			key_sucesor = (mi_nodo.GetId() + 2**0) % cant_nodos
			id_sucesor = finger[key_sucesor]["id"]
			ip_sucesor = finger[key_sucesor]["ip"]
			puerto_sucesor = finger[key_sucesor]["puerto"]		
			print(key_sucesor)
			print(mensaje["start"])
			if(key_sucesor != mensaje["start"]):
				print("holaaa")
				dir_sucesor = "tcp://"+ip_sucesor+":"+puerto_sucesor				
				solicitud = {"op": "Eliminar_nodo" , "id": mensaje["id"], "rxi": mensaje["rxi"], "ryi": mensaje["ryi"],"ip": mensaje["ip"], "puerto": mensaje["puerto"], "start": mensaje["start"],"stop":False}
				socket_sucesor.connect(dir_sucesor)
				socket_sucesor.send_json(solicitud)
				socket_sucesor.disconnect(dir_sucesor)



			
def main():
	#Solo para el ingreso del primer nodo del chord.
	if(len(sys.argv) == 3):
		my_ip = sys.argv[1]
		my_port = sys.argv[2]
		ide = random.randrange(0,cant_nodos-1)
		#ide=int(input("Id : "))
		print(ide)
		nuevo = Nodo(my_ip, my_port,ide)
		comp_x = ide + 1
		comp_y = ide

		nuevo.SetX(comp_x)
		nuevo.SetY(comp_y)
		nuevo.Finger()
		conectado = True
	#Se ejecuta del segundo nodo en adelante
	if(len(sys.argv) == 5):
		my_ip = sys.argv[1]
		my_port = sys.argv[2]
		ide = random.randrange(0,cant_nodos-1)
		#ide=int(input("Id : "))
		print(ide)
		print("\n")
		nuevo = Nodo(my_ip, my_port,ide)
		nuevo.Finger()

		other_ip = sys.argv[3]
		other_port = sys.argv[4]

		address = "tcp://"+other_ip+":"+other_port
		conectado = False

	#Se crea el contexto y se ejecuta el hilo de escucha.
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

		#Condicional ejecutada despues de saber donde se debe conectar el nodo.
		if(respuesta["op"] == "si"):
			print(respuesta["op"])
			nuevo.SetX(respuesta["x"])
			nuevo.SetY(respuesta["y"])
			print("Rango: "+str(nuevo.GetX()) +" -- "+ str(nuevo.GetY())+"\n")
			#Actualizando Finger
			new_finger = {}
			for i in range(0,pot):
				encontrado = False
				llave = (nuevo.GetId() + 2 ** i) % cant_nodos
				#print(llave)
				
				if(Verificar(llave,nuevo.GetX(),nuevo.GetY())):
					new_finger[llave] = {"id" : nuevo.GetId(), "ip": nuevo.GetIp() , "puerto" : nuevo.GetPuerto(), "rangollave" : {"x" :nuevo.GetX(), "y" : nuevo.GetY()}}
					#print("Me pertenece esta llave")
				else:
					#Llenado de finger table
					while not encontrado:
						socket_cliente.send_json({"op": "actualizando", "llave": llave})
						#print(llave)
						mensaje = socket_cliente.recv_json()
						#print(mensaje)
						if (mensaje["op"] == "es_llave"):
							new_finger[llave] = {"id" : mensaje["id"], "ip": mensaje["ip"] , "puerto" : mensaje["puerto"], "rangollave" : {"x" :mensaje["rx"], "y" :mensaje["ry"]}}
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

		#Condicion que se ejecuta cuando se necesita conectar al nodo siguiente de una finger_table de un nodo conocido
		elif(respuesta["op"] == "siguiente"):
			sgte_id =  respuesta["id"]
			sgte_ip = respuesta["ip"]
			sgte_port = respuesta["puerto"]
			socket_cliente.disconnect(address)
			address = "tcp://"+sgte_ip+":"+sgte_port

		#Si el nodo se encuentra conectado, y su fingerTable actualizada 
		if(conectado):
			sucesor_finger = nuevo.GetFinger()
			key_sucesor = (nuevo.GetId() + 2 ** 0) % cant_nodos
			xsucesor=sucesor_finger[key_sucesor]["rangollave"]["x"]
			ysucesor=sucesor_finger[key_sucesor]["rangollave"]["y"]

			sucesor={"id": sucesor_finger[key_sucesor]["id"], "ip": sucesor_finger[key_sucesor]["ip"], "puerto": sucesor_finger[key_sucesor]["puerto"]}
			solicitud = {"op": "rueda_la_bola" , "id": nuevo.GetId(), "rx": nuevo.GetX(), "ry": nuevo.GetY(),"rxi":xsucesor , "ryi": ysucesor, "ip": nuevo.GetIp(), "puerto": nuevo.GetPuerto(), "start": nuevo.GetId()}

			socket_cliente.disconnect(address)
			address = "tcp://"+sucesor["ip"]+":"+sucesor["puerto"]
			socket_cliente.connect(address)
			socket_cliente.send_json(solicitud)
			socket_cliente.recv_string()

	while conectado:
		print("Escoger la opcion:")
		print("1..Eliminar nodo")
		print("2..Subir Cancion")
		print("3..Bajar cancion")
		print("\n")
		
		op=int(input("Escoger la opcion:"))
		if(op==1):
			sucesor_finger = nuevo.GetFinger()
			key_sucesor = (nuevo.GetId() + 2 ** 0) % cant_nodos
			xsucesor=sucesor_finger[key_sucesor]["rangollave"]["x"]
			ysucesor=sucesor_finger[key_sucesor]["rangollave"]["y"]
			sucesor={"id": sucesor_finger[key_sucesor]["id"], "ip": sucesor_finger[key_sucesor]["ip"], "puerto": sucesor_finger[key_sucesor]["puerto"]}
			solicitud = {"op": "Eliminar_nodo" , "id": sucesor_finger[key_sucesor]["id"],"rxi":nuevo.GetX(), "ryi": ysucesor, "ip": sucesor_finger[key_sucesor]["ip"], "puerto":sucesor_finger[key_sucesor]["puerto"],"start":nuevo.GetX(),"stop":True}
			address = "tcp://"+sucesor["ip"]+":"+sucesor["puerto"]
			socket_cliente.connect(address)
			socket_cliente.send_json(solicitud)
			socket_cliente.recv_string()
			socket_cliente.disconnect(address)
			print("Termine")
			conectado=False


main()
