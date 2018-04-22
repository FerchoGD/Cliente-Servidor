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

	int primero=2,ultimo=8, numeromaquinas=4, tamintervalo;
	
	vector<int> elegidos;
	vector<double> kresultados;
	//zmqpp::context ctx;

	//zmqpp::socket_type typePull = zmqpp::socket_type::pull;
	//zmqpp::socket_type typePush = zmqpp::socket_type::push;



  	context ctx;


	socket canalserver(ctx,socket_type::rep);
	const string serverconexion = "tcp://*:4000";
	canalserver.bind(serverconexion);



	while (true) {

		if(ultimo - primero < numeromaquinas){
			cout<<"El K Optimo es: "<<elegidos[0]<<endl;
			break;
		}



		tamintervalo=ultimo/numeromaquinas;

		elegidos.push_back(primero);
		//Eligiendo los K's que necesitamos
		for(int j=0; j< numeromaquinas -1 ;j++){
			elegidos.push_back(primero+=tamintervalo);
		}


		

		//Calculando cada uno de los K
		#pragma omp parallel for
		for(int i=0; i<elegidos.size();i++){

			//Intercambio de datos

			

			string inicio;
			zmqpp::message saludo;
			canalserver.receive(saludo);

			saludo >> inicio;
			cout<<"Mensaje: "<<inicio<<endl;
			int puto=elegidos[i];
			string puntoya= to_string(puto);
			zmqpp::message enviok;
			
			enviok << puntoya;
			canalserver.send(enviok);

			string kresult;
			zmqpp::message msg;
			canalserver.receive(msg);

    		msg >> kresult;
    		
    		string chao="Bye";
    		zmqpp::message despido;
    		despido << chao;
    		canalserver.send(despido);

    		cout<<"Resultado del K: "<<kresult<<endl;
    		cout<<"Push back de: "<<atof(kresult.c_str())<<endl;
    		kresultados.push_back(atof(kresult.c_str()));		

		}

		canalserver.close();


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