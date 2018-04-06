import sys
import os


def main():
	i=1
	diccionario={}

	archivo=open("combined_data_1.txt")


	lineas=archivo.readlines()
	for linea in lineas:
		if(len(linea)< 10):
			datos=linea.split(":")
			pelicula=datos[0]

		else:
			datos=linea.split(",")
			if(not(datos[0] in diccionario)):
				print(linea)
				print(datos)
				diccionario[datos[0]]=[]
				diccionario[datos[0]].append((int(datos[1]),pelicula))
			else:
				diccionario[datos[0]].append((int(datos[1]),pelicula))


	#print(diccionario)


	resultado=open("users.txt","w")
	llaves=diccionario.keys()
	for llave in llaves:
		resultado.write(str(llave))
		resultado.write(" "+str(diccionario[llave]))
		resultado.write("\n")
	resultado.close()


if __name__ == '__main__':
	main()
