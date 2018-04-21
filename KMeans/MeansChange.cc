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


using namespace std;
using namespace zmqpp;


//Hallando el K-Óptimo
void Optimo(){

	int primero=2,ultimo=20, numeromaquinas=10, tamintervalo;
	
	vector<int> elegidos;
	vector<double> kresultados;
	//zmqpp::context ctx;

	//zmqpp::socket_type typePull = zmqpp::socket_type::pull;
	//zmqpp::socket_type typePush = zmqpp::socket_type::push;



  	context ctx;
  	socket canalserver(ctx,socket_type::rep);


	string ip="localhost";



	while (true) {

		tamintervalo=ultimo/numeromaquinas;
		elegidos.push_back(primero);
		//Eligiendo los K's que necesitamos
		for(int j=0; j< numeromaquinas ;j++){
			elegidos.push_back(primero+=tamintervalo);
		}


		if(elegidos[elegidos.size()-1] - elegidos[0] <= 1){
			cout<<"El K Optimo es: "<<elegidos[elegidos.size()-1]<<endl;
			break;
		}

		//Calculando cada uno de los K
		for(int i=0; i<elegidos.size();i++){

			//Conexion Server
			string kresult;
			const string serverconexion = "tcp://*:4000";
			canalserver.bind(serverconexion);

			string inicio;
			zmqpp::message saludo;
			canalserver.receive(saludo);

			saludo>>inicio;
			cout<<"Mensaje: "<<inicio<<endl;
			int puto=elegidos[i];
			string puntoya= to_string(puto);
			zmqpp::message enviok;
			
			enviok<<puntoya;
			canalserver.send(enviok);

			zmqpp::message msg;
			canalserver.receive(msg);

    		msg>>kresult;
    		

    		cout<<"Resultado del K: "<<kresult<<endl;
    		kresultados.push_back(atoi(kresult.c_str())/1.0);		
			canalserver.close();
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