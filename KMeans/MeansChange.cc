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


mutex counter_mutex;
//Funcion para ejecutar el hilo

void Server(socket &canalserver, vector<int>& Kelegidos, vector<double>& resultados, int &indice){

	

	while(indice < Kelegidos.size()){

		int ksito=Kelegidos[indice];
		string puntoya= to_string(ksito);
		zmqpp::message enviok;
		
		enviok << puntoya;
		canalserver.send(enviok);

		string kresult;
		zmqpp::message msg;
		canalserver.receive(msg);
		msg >> kresult;

		counter_mutex.lock();
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
		counter_mutex.unlock();
		cout<<std::this_thread::get_id()<<endl;
		std::this_thread::sleep_for(std::chrono::seconds(2));
	}
}


//Hallando el K-Óptimo
void Optimo(){

	int primero=1,ultimo=50,mitad=ultimo/2;
	
	vector<int> elegidos;
	vector<int> enviados;
	vector<double> kresultados;


  	context ctx;

	socket servidor(ctx,socket_type::rep);
	const string serverconexion = "tcp://*:4000";
	servidor.bind(serverconexion);
	int i=0;

	if(ultimo - primero < 2){
		cout<<"El K Optimo es: "<<ultimo<<endl;
	}



	mitad=(ultimo-primero)/2 + primero;

	//Eligiendo los K's que necesitamos

	elegidos.push_back(primero);
	elegidos.push_back(mitad);
	elegidos.push_back(ultimo);

	int op=1;

	while(true){

		

		string inicio;
		zmqpp::message saludo;
		servidor.receive(saludo);
		saludo >> inicio;
		cout<<"Mensaje: "<<inicio<<endl;


		if(inicio == "oe"){

			cout<<"Aqui estoy"<<endl;

			if(i<elegidos.size()){
				int ksito=elegidos[i];
				string puntoya= to_string(ksito);
				zmqpp::message enviok;
				enviados.push_back(elegidos[i]);
				enviok << puntoya;
				servidor.send(enviok);
			}

		}
		else{

			cout<<"Push back de: "<<atof(inicio.c_str())<<endl;
			if(atof(inicio.c_str())>0)
			{
				kresultados.push_back(atof(inicio.c_str()));	
			}
			if(enviados[enviados.size()-1] != elegidos[elegidos.size()-1]){
				if(kresultados.size() < elegidos.size()){
					int ksito=elegidos[i];
					string puntoya= to_string(ksito);
					zmqpp::message enviok;
					enviados.push_back(elegidos[i]);
					enviok << puntoya;
					servidor.send(enviok);
				
				}
			}
		}
		i++;
		int parte1,parte2,parte3;
		//cout<<"Tam elegidos: "<<elegidos.size()<<endl;
		//cout<<"Tam resultados: "<<kresultados.size()<<endl;
		if(enviados[enviados.size()-1] == elegidos[elegidos.size()-1]){

			if (op == 1){
				if(kresultados[0]-kresultados[1] > kresultados[1]-kresultados[2]){
					parte1=elegidos[1]/2;
					parte2=parte1-parte1/2;
					parte3=parte1+parte1/2;
			
				}
				else{
					parte1=elegidos[1]+elegidos[1]/2;
					parte2=elegidos[1]+elegidos[1]/4;
					parte3=parte1-elegidos[1]/4;
				}
				elegidos.clear();
				kresultados.clear();
				enviados.clear();
				elegidos.push_back(parte2);
				elegidos.push_back(parte1);
				elegidos.push_back(parte3);
				op=2;
			}
			else{
				mitad=kresultados[1];
				int Kchange=0;
				double Mchange=0;
				for(int j=0; j<kresultados.size()-1;j++){
					double change = (kresultados[j+1] - kresultados[j]) / (elegidos[j+1] - elegidos[j]);
					if(change>Mchange){
						Kchange=j;
						Mchange=change;
					}
				}
				primero=elegidos[Kchange];
				ultimo=elegidos[Kchange+1];
				elegidos.clear();
				kresultados.clear();
				enviados.clear();
				elegidos.push_back(primero);
				elegidos.push_back(mitad);
				elegidos.push_back(ultimo);

			}

			i=0;
		}

		

			
		

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