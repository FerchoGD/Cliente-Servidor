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


//Hallando el K-Óptimo
void Optimo(){

	int primero=2,ultimo=20, numeromaquinas=10;
	
	vector<int> elegidos;
	vector<double> kresultados;
	zmqpp::context ctx;

	zmqpp::socket_type typePull = zmqpp::socket_type::pull;
	zmqpp::socket_type typePush = zmqpp::socket_type::push;

	string myip="192.168.8.200";



	while (true) {

		tamintervalo=ultimo/numeromaquinas;
		elegidos.push_back(primero);
		//Eligiendo los K's que necesitamos
		for(int j=0; j<= numeromaquinas + 1;j++){
			elegidos.push_back(primero+=tamintervalo);
		}


		if(elegidos[elegidos.size()-1] - elegidos[0] <= 1){
			cout<<"El K Optimo es: "<<elegidos[elegidos.size()-1]<<endl;
			break;
		}

		//Calculando cada uno de los K
		for(int i=0; i<elegidos.size();i++){

			//Conexion Server
			const string serverconexion = "tcp://*:400"+i;
			zmqpp::socket canalserver (ctx, typePush);
			zmqpp::socket canalcliente (ctx, typePull);
			canalserver.bind(serverconexion);
			canalcliente.connect("tcp://"+myip+":3000");

			canalserver.send(elegidos[i]);
			zmqpp::message msg;
			canalcliente.recv(msg);
    		kresult=msg;
    		canalcliente.close();canalserver.close();
    		cout<<"Resultado del K: "<<kresult<<endl;
    		kresultados.push_back(kresult);		
		}


		//Mirando el cambio de pendiente
		int Kchange=0;
		double Mchange=0;
		for(int j=0; j<kresultados.size()-1;j++){
			double change = atan((kresultados[j+1] - kresultados[j]) / (elegidos[j+1] - elegidos[j])) ;
			if(change>Mchange){
				Kchange=j;
				Mchange=change;
			}

		}

		primero=elegidos[Kchange];
		ultimo=elegidos[Kchange+1];


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
    
    cout<<"hola"<<endl;
    Timer tTotal;    
    Optimo();
    cout << "Tiempo: " << tTotal.elapsed() << endl;
}