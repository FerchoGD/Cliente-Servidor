import hashlib
import random
import sys
import threading
import zmq
import os
import math
from time import sleep
cant_nodos = 1024
pot = int(math.log2(cant_nodos)) 
class Nodo():

	def __init__(self,ip,puerto,ide):
		self.id=ide
		self.finger_table = {}
		self.archivos = {}
		self.torrents = {}
		self.ip = ip
		self.address=""
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
	def GetArchivos(self):
		return self.archivos
	def SetArchivos(self,nuevos):
		self.archivos = nuevos
	def GetTorrents(self):
		return self.torrents
	def AddTorrent(self,nueva_llave, ip_pert, puerto_pert):
		self.torrents[nueva_llave] = {"ip": ip_pert, "puerto": puerto_pert}
	def SetTorrents(self, nuevos_torrents):
		self.torrents = nuevos_torrents
	def GetAddress(self):
		return self.address
	def SetAddress(self,address):
		self.address= address

	def Finger(self):
		for i in range(0,pot):
			llave = (self.id + 2 ** i) % cant_nodos
			self.finger_table[llave] = {"id" : self.id, "ip": self.ip, "puerto" : self.puerto, "rangollave" : {"x" :self.range_x, "y" : self.range_y}}

	#Recibiendo y actualizando con una nueva finger
	def Actualizar_Finger(self,table):
		for key in table:
			self.finger_table[key] = table[key]

	#Imprimir finger Table
	def Mostrar_Finger(self):
		for key in self.finger_table:
			print(str(key) +" Nodo: "+str(self.finger_table[key]["id"])+"  Ip: "+str(self.finger_table[key]["ip"])+"  Puerto: "+str(self.finger_table[key]["puerto"]))

	def Mostrar_Archivos(self):
		for key in self.archivos:
			print(str(key) +" "+str(self.archivos[key]))
			
	def Mostrar_Torrents(self):
		for key in self.torrents:
			print(str(key) +" "+str(self.torrents[key]))

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
def encontrarNodo(idMio,table,entrada_nodo_id,op):
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
		if(idMio != table[llave]["id"]):
			KeyFinal=llave
	##print("No estoy en la finger")
	sgte_id = table[KeyFinal]["id"]
	sgte_ip = table[KeyFinal]["ip"]
	sgte_port = table[KeyFinal]["puerto"]
	##print(str(sgte_id)+"  "+str(sgte_ip)+" "+str(sgte_port))
	if(op==1):
		data={"op" : "siguiente", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
	else:
		data={"op" : "no_es_llave", "id" : sgte_id, "ip": sgte_ip, "puerto": sgte_port}
	return data


def siguienteNodo(msj):
	sgte_id =  msj["id"]
	sgte_ip = msj["ip"]
	sgte_port = msj["puerto"]
	address = "tcp://"+sgte_ip+":"+sgte_port
	return address

#Funcion que se ejecuta en el hilo que queda esperando el ingreso de un mensaje
def Server(canal_servidor,canal_cliente,conectarNode1, port, mi_nodo,contexto):
	canal_servidor.bind("tcp://*:"+port)

	while True:
		mensaje = canal_servidor.recv_json()
		#print(mensaje)
		
		#condicional por medio del cual el nodo entrante busca su puesto en el chord
		if (mensaje["op"] == "ConectarNodoNuevo"):
			#print("\n")
			if(conectarNode1):
				ipn=mensaje['ip']
				portn=mensaje["puerto"]
				address = "tcp://"+ipn+":"+portn
				canal_cliente.connect(address)
				mi_nodo.SetAddress(address)
				conectarNode1=False
			#print("Se esta conectado a mi el nodo "+str(mensaje["id"]))
			entrada_nodo_id = mensaje["id"]
			aqui_es = Verificar(entrada_nodo_id, mi_nodo.GetX(), mi_nodo.GetY())
			#Si el nodo entrante esta en el rango de llaves del nodo de ingreso.
			if(aqui_es):
				data={"op": "si", "x":mi_nodo.GetX() , "y":entrada_nodo_id}
				mi_nodo.SetX((entrada_nodo_id+1) % cant_nodos)
				mi_nodo.SetY((mi_nodo.GetId())% cant_nodos)
				#print("Rango: "+str(mi_nodo.GetX()) +" - "+ str(mi_nodo.GetY()))	
			else:
				#print("Lo siento, te comunico con un nodo sucesor.")
				table = mi_nodo.GetFinger()
				data=encontrarNodo(mi_nodo.GetId(),table,entrada_nodo_id,1)
			canal_servidor.send_json(data)

		#cuando se conecte el nuevo nodo se le envia las cadenas con los torrent disponibles, para que puedan ser descargados.
		elif(mensaje["op"] == "EnviarTorrentCadenaNuevoNodo"):
			mensaje_envio = {"torrents": mi_nodo.GetTorrents()}
			canal_servidor.send_json(mensaje_envio)
		
		#Condicional que retorna el torrent-Archivo al nodo que lo este solicitando.
		elif(mensaje["op"] == "EnviarTorrentArchivo"):
			filename = mensaje["nombre_torrent"]
			envio = open(filename+".txt","rb+")
			info_to_send =  envio.read()
			canal_servidor.send(info_to_send)

		#Condicional para recibir el torrent_cadena en todos los nodos del chord.
		elif(mensaje["op"] == "toma_un_torrent"):
			archivo_to_recv = mensaje["nombre"]
			msj_ip = mensaje["ip"]
			msj_puerto = mensaje["puerto"]
			canal_servidor.send_string("recibido")
			mi_nodo.AddTorrent(archivo_to_recv, msj_ip, msj_puerto)
			#print("Torrent agregado..")
			#mi_nodo.Mostrar_Torrents()
			finger = mi_nodo.GetFinger()
			if(msj_puerto != finger[(mi_nodo.GetId() + 2 ** 0) % cant_nodos]["puerto"]):
				socket_sucesor = contexto.socket(zmq.REQ)
				key_sucesor = (mi_nodo.GetId() + 2**0) % cant_nodos
				ip_sucesor = finger[key_sucesor]["ip"]
				puerto_sucesor = finger[key_sucesor]["puerto"]
				dir_sucesor = "tcp://"+ip_sucesor+":"+puerto_sucesor
				solicitud = {"op": "toma_un_torrent" , "nombre": archivo_to_recv ,"ip": msj_ip, "puerto": msj_puerto}
				socket_sucesor.connect(dir_sucesor)
				socket_sucesor.send_json(solicitud)
				socket_sucesor.recv_string()
				socket_sucesor.disconnect(dir_sucesor)
		
	

		#Pasando los archivos al nuevo nodo que se conecta
		elif (mensaje["op"] == "roteme_partes"):
			archivos = mi_nodo.GetArchivos()
			archivos_to_send ={}
			print(archivos)
			if not archivos:
				#print("Diccionario de archivos vacios, nada para enviar")
				canal_servidor.send_json({"op": "nada_para_enviar"})
			else:
				for llave in archivos:
					if(Verificar(llave,mensaje["mi_x"], mi_nodo.GetX()-1)):
						print("Llave a rotar: "+str(llave))
						archivos_to_send[llave] = archivos[llave]
				canal_servidor.send_json({"op" : "rotando_partes", "lista_partes": archivos_to_send})
				canal_servidor.recv_string()
				#print("Archivos a enviar: ")
				#print(archivos_to_send)

				for llavesita in archivos_to_send:
					with open(archivos_to_send[llavesita], "rb") as entrada:
						#print(llavesita)
						info = entrada.read()
						canal_servidor.send(info)
						canal_servidor.recv_string()
						os.remove(archivos_to_send[llavesita])
						del archivos[llavesita]
				canal_servidor.send_string("Terminamos")

		elif(mensaje["op"] == "pasandote_partes"):
			mis_archivos = mi_nodo.GetArchivos()
			archivos_to_recv = mensaje["partes"]
			canal_servidor.send_string("mandame_partes")
			if not archivos_to_recv:
				print("Ningun archivo para recibir")
			else:
				for key in archivos_to_recv:
					mis_archivos[key] = archivos_to_recv[key]
					with open(archivos_to_recv[key], "ab+") as entrada:
						#print(key)
						info = canal_servidor.recv() 
						entrada.write(info)
						entrada.close()
						canal_servidor.send_string("siga")
				#print("Transferencia de archivos por SALIDA del nodo exitosa")
		#Condicional que nos permite actualizar la finger table del nodo que esta ingresando.
		elif(mensaje["op"] == "actualizando"):
			##print("Actualizando Inicio  --- Actualizando finger del nuevo")
			#mi_nodo.Mostrar_Finger()
			llave_check = mensaje["llave"]
			##print(llave_check)
			if(Verificar(llave_check, mi_nodo.GetX(), mi_nodo.GetY())):
				##print("SI estoy")
				msj = {"op": "es_llave", "id": mi_nodo.GetId(), "ip": mi_nodo.GetIp() , "puerto": mi_nodo.GetPuerto(), "rx" :mi_nodo.GetX(), "ry" : mi_nodo.GetY()}
			else:
				my_finger = mi_nodo.GetFinger()
				msj=encontrarNodo(mi_nodo.GetId(),my_finger,llave_check,2)
			canal_servidor.send_json(msj)
			##print("Actualizando Fin")
		#Condicional que ejecuta la orden de actualizacion de las finger tables.
		elif(mensaje["op"] == "rueda_la_bola"):
			#Actualizando Finger
			finger = mi_nodo.GetFinger()
			for key in finger:
				if(Verificar(key, mensaje["rx"], mensaje["ry"])):
					finger[key]["id"] = mensaje["id"]
					finger[key]["ip"] = mensaje["ip"]
					finger[key]["puerto"] = mensaje["puerto"]
					finger[key]["rangollave"]={"x": mensaje["rx"],"y":mensaje["ry"]}

			canal_servidor.send_string("Listo")
			#print("Rodando la bola")
			mi_nodo.Actualizar_Finger(finger)
			#mi_nodo.Mostrar_Finger()			

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
			#print("Rango: "+str(mi_nodo.GetX()) +" - "+ str(mi_nodo.GetY()))
			finger = mi_nodo.GetFinger()
			for key in finger:
				if(Verificar(key, mensaje["rxi"], mensaje["ryi"])):
					finger[key]["id"] = mensaje["id"]
					finger[key]["ip"] = mensaje["ip"]
					finger[key]["puerto"] = mensaje["puerto"]
					finger[key]["rangollave"]={"x": mensaje["rxi"],"y":mensaje["ryi"]}

			canal_servidor.send_string("Listo")
			#print("Eliminar_nodo")
			mi_nodo.Actualizar_Finger(finger)
			#mi_nodo.Mostrar_Finger()	
			socket_sucesor = contexto.socket(zmq.REQ)
			key_sucesor = (mi_nodo.GetId() + 2**0) % cant_nodos
			id_sucesor = finger[key_sucesor]["id"]
			ip_sucesor = finger[key_sucesor]["ip"]
			puerto_sucesor = finger[key_sucesor]["puerto"]		
			#print(key_sucesor)
			#print(mensaje["start"])
			if(key_sucesor != mensaje["start"]):
				#print("holaaa")
				dir_sucesor = "tcp://"+ip_sucesor+":"+puerto_sucesor				
				solicitud = {"op": "Eliminar_nodo" , "id": mensaje["id"], "rxi": mensaje["rxi"], "ryi": mensaje["ryi"],"ip": mensaje["ip"], "puerto": mensaje["puerto"], "start": mensaje["start"],"stop":False}
				socket_sucesor.connect(dir_sucesor)
				socket_sucesor.send_json(solicitud)
				socket_sucesor.disconnect(dir_sucesor)

		elif(mensaje["op"]=="cargar_parte"):
			if(Verificar(mensaje["llave"], mi_nodo.GetX(), mi_nodo.GetY())):
				#print("HOla")
				mensaje = {"op":"enviela"}
				canal_servidor.send_json(mensaje)

			else:
				table = mi_nodo.GetFinger()
				data=encontrarNodo(mi_nodo.GetId(),table,mensaje["llave"],1)
				canal_servidor.send_json(data)

		elif(mensaje["op"] == "enviando_parte"):

			key = mensaje["llave"]
			archivo = mensaje["nombre_archivo"]
			parte = mensaje["parte"]
			canal_servidor.send_string("Listo")
			info_parte = canal_servidor.recv()
			canal_servidor.send_string("fin")
			mis_archivos = mi_nodo.GetArchivos()
			mis_archivos[key] = archivo+parte
			with open(archivo+parte,"ab+") as output:
				output.write(info_parte)
			mi_nodo.SetArchivos(mis_archivos)
			#mi_nodo.Mostrar_Archivos()

		elif(mensaje["op"] == "solicito_parte"):
			if(Verificar(int(mensaje["llave"]), mi_nodo.GetX(), mi_nodo.GetY())):
				data_parte = open(mensaje["parte"],"rb")
				info_parte = data_parte.read()
				mensaje = {"op":"recibela"}
				canal_servidor.send_json(mensaje)
				canal_servidor.recv_string()
				canal_servidor.send(info_parte)

			else:
				table = mi_nodo.GetFinger()
				data=encontrarNodo(mi_nodo.GetId(),table,int(mensaje["llave"]),1)
				canal_servidor.send_json(data)

	
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
		conectarNode1=True
	#Se ejecuta del segundo nodo en adelante
	if(len(sys.argv) == 5):
		my_ip = sys.argv[1]
		my_port = sys.argv[2]
		ide = random.randrange(0,cant_nodos-1)
		#ide=int(input("Id : "))
		print(ide)
		#print("\n")
		nuevo = Nodo(my_ip, my_port,ide)
		nuevo.Finger()

		other_ip = sys.argv[3]
		other_port = sys.argv[4]

		address = "tcp://"+other_ip+":"+other_port
		conectado = False
		conectarNode1=False

	#Se crea el contexto y se ejecuta el hilo de escucha.
	context= zmq.Context()
	socket_cliente = context.socket(zmq.REQ)
	socket_servidor = context.socket(zmq.REP)
	thread_server = threading.Thread(target=Server, args=(socket_servidor,socket_cliente,conectarNode1, my_port, nuevo, context))
	thread_server.start()

	#Ciclo para conectar nodo
	while not conectado:

		socket_cliente.connect(address)

		data = {"op" : "ConectarNodoNuevo","id" : nuevo.GetId(), "ip" : nuevo.GetIp(), "puerto" : nuevo.GetPuerto()}
		socket_cliente.send_json(data)
		respuesta = socket_cliente.recv_json()

		#Condicional ejecutada despues de saber donde se debe conectar el nodo.
		if(respuesta["op"] == "si"):
			#print(respuesta["op"])
			nuevo.SetX(respuesta["x"])
			nuevo.SetY(respuesta["y"])
			#print("Rango: "+str(nuevo.GetX()) +" -- "+ str(nuevo.GetY())+"\n")
			#Actualizando Finger
			new_finger = {}
			for i in range(0,pot):
				encontrado = False
				llave = (nuevo.GetId() + 2 ** i) % cant_nodos
				##print(llave)
				
				if(Verificar(llave,nuevo.GetX(),nuevo.GetY())):
					new_finger[llave] = {"id" : nuevo.GetId(), "ip": nuevo.GetIp() , "puerto" : nuevo.GetPuerto(), "rangollave" : {"x" :nuevo.GetX(), "y" : nuevo.GetY()}}
					##print("Me pertenece esta llave")
				else:
					#Llenado de finger table
					while not encontrado:
						socket_cliente.send_json({"op": "actualizando", "llave": llave})
						##print(llave)
						mensaje = socket_cliente.recv_json()
						##print(mensaje)
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
			#print("\n")
			#print("He Actualizado mi finger con exito"+"\n")
			#nuevo.Mostrar_Finger()
			conectado=True

		#Condicion que se ejecuta cuando se necesita conectar al nodo siguiente de una finger_table de un nodo conocido
		elif(respuesta["op"] == "siguiente"):
			socket_cliente.disconnect(address)
			address = siguienteNodo(respuesta)
		#Si el nodo se encuentra conectado, y su fingerTable actualizada 
		if(conectado):
			sucesor_finger = nuevo.GetFinger()
			key_sucesor = (nuevo.GetId() + 2 ** 0) % cant_nodos
			xsucesor=sucesor_finger[key_sucesor]["rangollave"]["x"]
			ysucesor=sucesor_finger[key_sucesor]["rangollave"]["y"]

			sucesor={"id": sucesor_finger[key_sucesor]["id"], "ip": sucesor_finger[key_sucesor]["ip"], "puerto": sucesor_finger[key_sucesor]["puerto"]}
			solicitud = {"op": "rueda_la_bola" , "id": nuevo.GetId(), "rx": nuevo.GetX(), "ry": nuevo.GetY(),"rxi":xsucesor , "ryi": ysucesor, "ip": nuevo.GetIp(), "puerto": nuevo.GetPuerto(), "start": nuevo.GetId()}
			socket_cliente.disconnect(address)
			aux=nuevo.GetX() + (2 ** (pot-1))
			data=encontrarNodo(nuevo.GetId(),nuevo.GetFinger(),aux,1)
			address = "tcp://"+data["ip"]+":"+data["puerto"]
			socket_cliente.connect(address)
			socket_cliente.send_json(solicitud)
			socket_cliente.recv_string()

			#Recibiendo los archivos que me corresponden
			#print("Empezando a rotar archivos...")
			socket_cliente.disconnect(address)
			address = "tcp://"+sucesor["ip"]+":"+sucesor["puerto"]
			socket_cliente.connect(address)
			solicitud_partes = {"op": "roteme_partes","mi_x":nuevo.GetX()}
			socket_cliente.send_json(solicitud_partes)
			responde = socket_cliente.recv_json()

			if(responde["op"] == "rotando_partes"):
				partes = responde["lista_partes"]
				nuevo.SetArchivos(partes)
				socket_cliente.send_string("Mandelas")
				#print("Partes Recibidas son: ")
				#print(partes)
				for llave in partes:
					with open(partes[llave], "ab+") as entrada:
						#print("Recibiendo info parte..."+llave)
						info = socket_cliente.recv()
						socket_cliente.send_string("Siga")
						entrada.write(info)
						entrada.close()
				socket_cliente.recv_string()
			elif(responde["op"] ==  "nada_para_enviar"):
				pass
				#print("No hay archivos para recibir")

			#print("Recibiendo torrents existentes")
			solicitud_torrents = {"op": "EnviarTorrentCadenaNuevoNodo"}
			socket_cliente.send_json(solicitud_torrents)
			torrents_to_recv = socket_cliente.recv_json()
			nuevo.SetTorrents(torrents_to_recv["torrents"])
			#nuevo.Mostrar_Torrents()




	while conectado:
		print("\n")
		print("Escoger la opcion:")
		print("1..Eliminar nodo")
		print("2..Subir archivo")
		print("3..Bajar archivo")
		print("4..Mostrar mi Finger Table")
		print("\n")
		
		op=int(input("Escoger la opcion:"))
		print("\n")

		if(op==1):
			if(not(conectarNode1)):
				socket_cliente.disconnect(address)
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
			#print("Pasando los archivos...")
			archivos = nuevo.GetArchivos()

			solicitud_partes = {"op": "pasandote_partes","partes":archivos}
			socket_cliente.send_json(solicitud_partes)
			responde = socket_cliente.recv_string()

			if(responde == "mandame_partes"):
				#print("Partes a enviar son: ")
				#print(archivos)
				for llave in archivos:
					with open(archivos[llave], "rb+") as entrada:
						#print("Enviando info parte..."+str(llave))
						info = entrada.read()
						socket_cliente.send(info)
						socket_cliente.recv_string()
						entrada.close()
						os.remove(archivos[llave])

			socket_cliente.disconnect(address)
			#print("Termine")
			conectado=False
			break
			sys.exit()

		if(op==2):
			filename = input("Digite el nombre del archivo: ")
			extension =  input("Digite la extension del archivo: ")

			resultados = open(filename+".txt","ab+")

			with open(filename+extension, "rb") as entrada:
				data = entrada.read()
				tam = entrada.tell()
				lim=tam/(1024*1024)
				#print("Tamaño: "+ str(tam))
				parts=int(lim+1)
				i=0
				#print ("Partes: "+ str(parts))
				entrada.seek(0)
				archivos_nuevos = nuevo.GetArchivos()
				while i<=lim:
					enviado = False
					key = int(random.uniform(0,cant_nodos-1))
					to_write = str(key)+"-"+filename+str(i+1)+extension+"\n"
					resultados.write(to_write.encode('utf-8'))
					#print("Parte en el ID: "+str(key))					

					if(Verificar(key,nuevo.GetX(),nuevo.GetY())):
						archivos_nuevos[key] = filename+str(i+1)+extension
						data_part=entrada.read(1024*1024)
						with open(filename+str(i+1)+extension,"ab+") as output:	
							output.write(data_part)
					else:
						data={"op": "cargar_parte", "llave": key}
						finger=nuevo.GetFinger()

						if(conectarNode1):
							address=nuevo.GetAddress()
							conectarNode1=False						

						socket_cliente.disconnect(address)

						encontrado=False
						for key1 in finger:
							if(Verificar(key, finger[key1]["rangollave"]["x"], finger[key1]["rangollave"]["y"])):
								ips = finger[key1]["ip"]
								ports = finger[key1]["puerto"]
								encontrado = True
						if(not(encontrado)):
							datos_sgte = encontrarNodo(nuevo.GetId(),finger,key,1)
							ips = datos_sgte["ip"]
							ports = datos_sgte["puerto"]
						address = "tcp://"+ips+":"+ports			
						socket_cliente.connect(address)

						while not enviado:				
							
							socket_cliente.send_json(data) 
							msj=socket_cliente.recv_json()
							if(msj["op"] == "enviela"):
								data_part=entrada.read(1024*1024)
								msj={"op" : "enviando_parte", "nombre_archivo":filename,"parte":str(i+1)+str(extension),"llave":key}
								socket_cliente.send_json(msj)

								socket_cliente.recv_string()
								socket_cliente.send(data_part)
								socket_cliente.recv_string()
								enviado = True
								#print("Enviado con exito")

							elif(msj["op"] == "siguiente"):								
								if(conectarNode1):
									address=nuevo.GetAddress()
								socket_cliente.disconnect(address)
								address = siguienteNodo(msj)
								socket_cliente.connect(address)
						#print("Enviada")		
					i+=1
				nuevo.SetArchivos(archivos_nuevos)
			resultados.close()
			#nuevo.Mostrar_Archivos()
			
			#print("Partes enviadas")
			nuevo.AddTorrent(filename, nuevo.GetIp(), nuevo.GetPuerto())
			torrent = {"op":"toma_un_torrent", "nombre": filename, "ip": nuevo.GetIp(), "puerto": nuevo.GetPuerto()}			
			socket_cliente.disconnect(address)
			sucesor_finger = nuevo.GetFinger()
			key_sucesor = (nuevo.GetId() + 2 ** 0) % cant_nodos
			sucesor_ip = sucesor_finger[key_sucesor]["ip"]
			sucesor_puerto = sucesor_finger[key_sucesor]["puerto"]
			address = "tcp://"+sucesor_ip+":"+sucesor_puerto
			socket_cliente.connect(address)
			socket_cliente.send_json(torrent)
			socket_cliente.recv_string()
			#print("Torrent enviado...")
			resultados.close()





		if(op==3):
			filename = input("Digite el nombre del archivo: ")
			extension = input("Digite la extension del archivo")
			resultado = open(filename+extension,"ab+")

			if not (os.path.isfile(filename+".txt")):
				ip_connect = nuevo.GetTorrents()[filename]["ip"]
				puerto_connect = nuevo.GetTorrents()[filename]["puerto"]
				if(conectarNode1):
					address=nuevo.GetAddress()
					conectarNode1=False					
				socket_cliente.disconnect(address)
				address = "tcp://"+ip_connect+":"+puerto_connect
				socket_cliente.connect(address)
				socket_cliente.send_json({"op":"EnviarTorrentArchivo", "nombre_torrent": filename})
				info = socket_cliente.recv()
				archivo = open(filename+".txt","ab+")
				archivo.write(info)
				archivo.close()

			archivo = open(filename+".txt")
			lineas = archivo.readlines()
			for linea in lineas:
				datos = linea.split("-")
				llave = datos[0]
				otros = datos[1].split("\n")
				parte = otros[0]

				if(Verificar(int(llave),nuevo.GetX(),nuevo.GetY())):
					data_parte = open(parte,"rb")
					info_parte = data_parte.read()
					resultado.write(info_parte)

				else:
					data={"op": "solicito_parte", "llave": llave, "parte": parte}
					recibido = False
					finger=nuevo.GetFinger()
					
					datos_sgte = encontrarNodo(nuevo.GetId(),finger,int(llave),1)
					ips = datos_sgte["ip"]
					ports = datos_sgte["puerto"]
					
					socket_cliente.disconnect(address)
					address = "tcp://"+ips+":"+ports
					socket_cliente.connect(address)

					while not recibido:									
						socket_cliente.send_json(data) 
						msj=socket_cliente.recv_json()
						if(msj["op"] == "recibela"):
							socket_cliente.send_string("Damela")
							info_parte = socket_cliente.recv()
							resultado.write(info_parte)
							recibido = True
							#print("Recibido con exito")

						elif(msj["op"] == "siguiente"):
							if(conectarNode1):
									address=nuevo.GetAddress()
							socket_cliente.disconnect(address)
							address = siguienteNodo(msj)
							socket_cliente.connect(address)

		if(op==4):
			print("Mis Datos")
			print("Id: " + str(nuevo.GetId())+"  "+"Ip: "+str(nuevo.GetIp())+"  "+"Puerto: "+str(nuevo.GetPuerto()))
			print("Rango: " + "(" + str(nuevo.GetX())+" - "+ str(nuevo.GetY())+ ")")
			nuevo.Mostrar_Finger()

		if(op==5):
			nuevo.Mostrar_Archivos()

		if(op==6):
			nuevo.Mostrar_Torrents()

main()
