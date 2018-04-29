#include <iostream>
#include <cstdlib>
#include <fstream>
#include <string>
#include <utility>
#include <string.h>
#include <vector>
#include <tuple>
#include <math.h>
#include <cstdlib>
#include "timer.hh"
#include <zmqpp/zmqpp.hpp>
#include <thread>


using namespace std;
using namespace zmqpp;

//Funcion para ejecutar el hilo

void Server(socket &canalserver, vector<int>& Kelegidos, vector<double>& resultados, int &indice, string verificar){

	if(verificar=="primero"){
		string inicio;
		zmqpp::message saludo;
		canalserver.receive(saludo);
		saludo >> inicio;
		cout<<"Mensaje: "<<inicio<<endl;
	}

	while(true){



		int ksito=Kelegidos[indice];
		string puntoya= to_string(ksito);
		zmqpp::message enviok;
		
		enviok << puntoya;
		canalserver.send(enviok);

		string kresult;
		zmqpp::message msg;
		canalserver.receive(msg);

		msg >> kresult;

		if(kresult!="oe"){
		
			string chao="Bye";
			zmqpp::message despido;
			despido << chao;
			//canalserver.send(despido);

			cout<<"Push back de: "<<atof(kresult.c_str())<<endl;
			if(atof(kresult.c_str())>0)
			{
				resultados.push_back(atof(kresult.c_str()));
				indice++;		
			}

		}
		else{
			indice++;
		}
	}
}


//Hallando el K-Óptimo
void Optimo(){

	int primero=1,ultimo=20,mitad=ultimo/2;
	
	vector<int> elegidos;
	vector<double> kresultados;
	//zmqpp::context ctx;

	//zmqpp::socket_type typePull = zmqpp::socket_type::pull;
	//zmqpp::socket_type typePush = zmqpp::socket_type::push;



  	context ctx;

	socket servidor(ctx,socket_type::rep);
	const string serverconexion = "tcp://*:4000";
	servidor.bind(serverconexion);

	string saludo="primero";
	



	while (true) {

		

		if(ultimo - primero < 2){
			cout<<"El K Optimo es: "<<ultimo<<endl;
			break;
		}



		mitad=(ultimo-primero)/2 + primero;

		//Eligiendo los K's que necesitamos

		elegidos.push_back(primero);
		elegidos.push_back(mitad);
		elegidos.push_back(ultimo);


		//Calculando cada uno de los K

		
		for(int i=0; i<elegidos.size();){

			//Intercambio de datos

			thread thread_server;
			thread_server = thread(Server, ref(servidor), ref(elegidos), ref(kresultados), ref(i),saludo);
			thread_server.join();

			
		}



		//Mirando el cambio de pendiente
		int Kchange=0;
		double Mchange=0;
		for(int j=0; j<kresultados.size()-1;j++){
			double change = (kresultados[j+1] - kresultados[j]) / (elegidos[j+1] - elegidos[j]) ;
			if(change>Mchange){
				Kchange=j;
				Mchange=change;
			}

		}

		primero=elegidos[Kchange];
		ultimo=elegidos[Kchange+1];
		saludo="segundo";




		elegidos.clear();
		kresultados.clear();
		
	}

	
}


int main()
{	
	srand(time(NULL)); 
	

    /*
    cout << "Tamaño de puntos: " << points.size() << endl;
    cout <<  "Ultimo punto" << endl;
    for(int i = 0; i < points[114551-1].getTotalPeliculas(); i++)
    	cout << points[114551-1].getPair(i).first << " " << points[114551-1].getPair(i).second << endl;*/
    
    Timer tTotal;    
    Optimo();
    cout << "Tiempo: " << tTotal.elapsed() << endl;
}