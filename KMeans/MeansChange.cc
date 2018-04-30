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
int parte1,parte2,parte3,parte4,parte5,parte6;
void Repartir(vector <int> &elegidos,vector <int> &enviados, vector<pair <double,int>> &kresultados){
		parte1=elegidos[1]/2;
		parte2=parte1-parte1/2;
		parte3=parte1+parte1/2;
		parte4=elegidos[1]+elegidos[1]/2;
		parte5=elegidos[1]+elegidos[1]/4;
		parte6=parte4+elegidos[1]/4;
		elegidos.clear();
		enviados.clear();
		kresultados.clear();
		elegidos.push_back(parte2);
		elegidos.push_back(parte1);
		elegidos.push_back(parte3);
		elegidos.push_back(parte4);
		elegidos.push_back(parte5);
		elegidos.push_back(parte6);
	}

bool verificar(vector<pair <double,int>> &kdos,int &ultimo){

	for(int i=0;i< kdos.size();i++){
		if(kdos[i].second == ultimo){
			return true;
		}
	}
	return false;
}

//Hallando el K-Óptimo
void Optimo(){

	int primero=1,ultimo=20,mitad=ultimo/2;
	
	vector<int> elegidos;
	vector<int> enviados;
	vector<pair <double,int>> kresultados;
	vector<pair <double,int>> kdos;

	pair<double,int> pareja;


  	context ctx;

	socket servidor(ctx,socket_type::rep);
	const string serverconexion = "tcp://*:4002";
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
	int ca=0;
	int divi =16; 

	while(true){

		

		string inicio;
		zmqpp::message saludo;
		servidor.receive(saludo);
		saludo >> inicio;
		string resultado, k;
		
	    for(int t=0;t< inicio.size();t++){
	    	if(inicio[t]=='-'){
	    		ca=t+1;
	    		break;
	    	}
	    	else{
	    		resultado+= inicio[t];
	    	}
	    }
	    for(;ca< inicio.size();ca++){
	    	if(inicio[ca]==' '){
	    		break;
	    	}
	    	else{
	    		k+= inicio[ca];
	    	}
	    }
	    pareja.first=atof(resultado.c_str());
	    pareja.second=atof(k.c_str());
	    if (inicio != "oe"){
	    	cout<<"resultado: "<<pareja.first<<endl;
			cout<<"k: "<<pareja.second<<endl;
		}
		
		if(inicio == "oe"){

			//cout<<"Aqui estoy"<<endl;

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
				kresultados.push_back(pareja);
				kdos.push_back(pareja);	
			}
			int ksito;
			bool a=verificar(kdos,elegidos[i]);
			if (a)
				ksito=elegidos[i+1];
			else
				ksito=elegidos[i];
			string puntoya= to_string(ksito);
			zmqpp::message enviok;
			enviados.push_back(elegidos[i]);
			enviok << puntoya;
			servidor.send(enviok);
			
				
			
		}
		i++;
		//cout<<"Tam elegidos: "<<elegidos.size()<<endl;
		//cout<<"Tam resultados: "<<kresultados.size()<<endl;
		if(enviados[enviados.size()-1] == elegidos[elegidos.size()-1]){

			if (op == 1){

				Repartir(elegidos,enviados,kresultados);
				op=2;
			}
			else{
				if(verificar(kdos,ultimo)){

					int aux=ultimo/divi;
					int ban=aux;
					if (aux < 1)
						break;
					elegidos.clear();
					kresultados.clear();
					enviados.clear();
					for(int i=0;i<divi;i++){
						cout<< aux <<"  aux "<< endl;
						elegidos.push_back(aux);
						aux=aux+ban;
					}
				}
			}

			i=0;
		}

	}
}


int main()
{	
	srand(time(NULL)); 
	
    
    Timer tTotal;    
    Optimo();
    cout << "Tiempo: " << tTotal.elapsed() << endl;
}