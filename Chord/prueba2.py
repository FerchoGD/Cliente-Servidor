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

	
def encontrar(table,entrada_nodo_id,idn):
	banderaKeyFinal= -1
	
	for llave in table:
		print(llave)
		print(idn)
		print(table[llave]["id"])


		if(table[llave]["id"] == idn):
			sgte_id = table[KeyFinal]["id"]
			sgte_ip = table[KeyFinal]["ip"]
			sgte_port = table[KeyFinal]["puerto"]
			data={"op" : "siguiente", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
			return data

		if(banderaKeyFinal > table[llave]["id"]):
			sgte_id = table[llave]["id"]
			sgte_ip = table[llave]["ip"]
			sgte_port = table[llave]["puerto"]
			data={"op" : "siguiente", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
			return data
			
		if(table[llave]["id"] > entrada_nodo_id):
			print("Noooo")
			sgte_id = table[llave]["id"]
			sgte_ip = table[llave]["ip"]
			sgte_port = table[llave]["puerto"]
			data={"op" : "siguiente", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
			return data
					
		banderaKeyFinal=table[llave]["id"]
		KeyFinal=llave


	print("No estoy ")
	sgte_id = table[KeyFinal]["id"]
	sgte_ip = table[KeyFinal]["ip"]
	sgte_port = table[KeyFinal]["puerto"]
	print(str(sgte_id)+"  "+str(sgte_ip)+" "+str(sgte_port))
	data={"op" : "siguiente", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
	return data



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
				# if(mi_nodo.GetId() > entrada_nodo_id):

				data={"op": "si", "x":mi_nodo.GetX() , "y":entrada_nodo_id}
				mi_nodo.SetX((entrada_nodo_id+1) % cant_nodos)
				mi_nodo.SetY((mi_nodo.GetId())% cant_nodos)
				print("Rango: "+str(mi_nodo.GetX()) +" - "+ str(mi_nodo.GetY()))
					
			else:
				table = mi_nodo.GetFinger()
				idn=mi_nodo.GetId()
				data=encontrar(table,entrada_nodo_id,idn)
			canal_servidor.send_json(data)	

		elif(mensaje["op"] == "actualizando"):
			print("Actualizando Inicio  --- Actualizando finger del nuevo")
			#mi_nodo.Mostrar_Finger()
			llave_check = mensaje["llave"]

			print(llave_check)
			if(Verificar(llave_check, mi_nodo.GetX(), mi_nodo.GetY())):
				msj = {"op": "es_llave", "id": mi_nodo.GetId(), "ip": mi_nodo.GetIp() , "puerto": mi_nodo.GetPuerto(), "rx" :mi_nodo.GetX(), "ry" : mi_nodo.GetY()}
			else:
				my_finger = mi_nodo.GetFinger()
				Stop1 = True
				Stop2 = True
				banderaKeyFinal=-1
				for key in  my_finger:
					if(Stop2):
						if(banderaKeyFinal > my_finger[key]["id"]):
							sgte_id = my_finger[key]["id"]
							sgte_ip = my_finger[key]["ip"]
							sgte_port = my_finger[key]["puerto"]
							Stop1=False
							Stop2 = False
					if(Stop2):
						if( my_finger[key]["id"] >= llave_check):
							if(Stop1):
								sgte_id = my_finger[key]["id"]
								sgte_ip = my_finger[key]["ip"]
								sgte_port = my_finger[key]["puerto"]
								Stop1=False
								Stop2 = False
					banderaKeyFinal=my_finger[key]["id"]
					KeyFinal=key
				if(Stop1):
					print("No estoy ")
					sgte_id = my_finger[KeyFinal]["id"]
					sgte_ip = my_finger[KeyFinal]["ip"]
					sgte_port = my_finger[KeyFinal]["puerto"]
					print(str(sgte_id)+"  "+str(sgte_ip)+" "+str(sgte_port))



				msj = {"op": "no_es_llave", "id": sgte_id, "ip": sgte_ip , "puerto": sgte_port}
			canal_servidor.send_json(msj)
			print("Actualizando Fin")


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
				
				print(key)
				print(mensaje["rxi"])
				print(mensaje["ryi"])

				if(Verificar(key, mensaje["rxi"], mensaje["ryi"])):
					print("Siiiiiiiiii")
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
					new_finger[llave] = {"id" : nuevo.GetId(), "ip": nuevo.GetIp() , "puerto" : nuevo.GetPuerto(), "rangollave" : {"x" :nuevo.GetX(), "y" : nuevo.GetY()}}
					print("Me pertenece esta llave")
				else:
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

		elif(respuesta["op"] == "siguiente"):
			sgte_id =  respuesta["id"]
			sgte_ip = respuesta["ip"]
			sgte_port = respuesta["puerto"]
			socket_cliente.disconnect(address)
			address = "tcp://"+sgte_ip+":"+sgte_port


	

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


main()
