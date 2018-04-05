import sys
import os


def main():
	i=1
	diccionario={}
	while(i<1000):
		if(i<10):
			archivo=open("mv_000000"+str(i)+".txt")
		elif(i<100):
			archivo=open("mv_00000"+str(i)+".txt")
		elif(i<1000):
			archivo=open("mv_0000"+str(i)+".txt")

		
		lineas=archivo.readlines()
		for linea in lineas:
			datos=linea.split(",")
			if(linea!=str(i)+":\n" and not(datos[0] in diccionario)):
				print(linea)
				print(datos)
				diccionario[datos[0]]=[]
				diccionario[datos[0]].append((int(datos[1]),i))
			elif(datos[0] in diccionario):
				diccionario[datos[0]].append((int(datos[1]),i))

		i+=1
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
