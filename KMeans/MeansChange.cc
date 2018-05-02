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

bool evaluar(vector <int> &elegidos,vector <int> &enviados,vector <double> &kresultados,int &primero,int &mitad,int &ultimo,int divi){
	double Var1= atan((kresultados[primero]-kresultados[mitad])/(mitad-primero)) * 180 / M_PI;
	double Var2= atan((kresultados[mitad]-kresultados[ultimo])/(ultimo-mitad)) * 180 / M_PI;
	double valor1;
	double valor2;
	int ult=ultimo;
	int pri=primero;
	int aux;
	if(Var1 > 45)
		valor1=Var1-45;
	else
		valor1=45-Var1;
	if(Var2 > 45)
		valor2=Var2-45;
	else
		valor2=45-Var2;
	cout<< valor1<<"--------------------------------"<<valor2<<endl;
	if(valor1 <= valor2){
		ultimo=mitad;
		mitad=ultimo/2;
	}
	else{
		primero=mitad;
		mitad=ultimo-(mitad/2);
	}
	elegidos.clear();
	enviados.clear();
	aux=(ult-pri)/divi;
	int ban=aux;
	if (aux <= 1)
		return true;
	cout << "ultimo "<<ultimo<< "Mitad " <<mitad <<"  divi "<<divi<<" aux --------"<< aux <<endl;
	for(int i=0;primero + aux<ultimo;i++){
		//cout<< aux <<"  aux "<< endl;
		elegidos.push_back(aux);
		aux=aux+ban;

	}
	return false;
}

void Repartir(vector <int> &elegidos,vector <int> &enviados, int ultimo, int divi){
	int aux=ultimo/divi;
	int ban=aux;
	elegidos.clear();
	enviados.clear();
	for(int i=0;aux<ultimo;i++){
		//cout<< aux <<"  aux "<< endl;
		elegidos.push_back(aux);
		aux=aux+ban;
	}
}

bool verificar(vector <double> &kdos,int &ultimo){

	if(kdos[ultimo] != '\0'){
			return true;
		}
	
	return false;
}

bool verificar2(vector<int> &enviados,int &ultimo){

	for(int i=0;i< enviados.size();i++){
		if(enviados[i] == ultimo){
			return true;
		}
	}
	return false;
}

void mostrarVectores(vector <double> &kresultados,vector<int> &enviados,vector<int> &elegidos){
	cout << "enviados"<<endl;
	for (int o=0;o < enviados.size();o++){
		if(enviados[o] != '\0' )
			cout << enviados[o] <<"-";
	}
	cout<<endl;
	cout << "elegidos"<<endl;
	for (int o=0;o < elegidos.size();o++){
		if(elegidos[o] != '\0' )
			cout << elegidos[o] <<"-";
	}
	cout<<endl;
	cout << "kresultados"<<endl;
	for (int o=0;o < kresultados.size();o++){
		if(kresultados[o] != '\0' )
			cout << o <<"-";
	}
	cout << endl;
}

void mensajeRec(pair <double,int> &pareja,int &banMensaje, string&k, string &resultado,string &inicio){
	for(int t=0;t< inicio.size();t++){
    	if(inicio[t]=='-'){
    		banMensaje=t+1;
    		break;
    	}
    	else{
    		resultado+= inicio[t];
    	}
    }
    for(;banMensaje< inicio.size();banMensaje++){
    	if(inicio[banMensaje]==' '){
    		break;
    	}
    	else{
    		k+= inicio[banMensaje];
    	}
    }
    pareja.first=atof(resultado.c_str());
    pareja.second=atof(k.c_str());
	cout<<"resultado: "<<pareja.first<<endl;
	cout<<"k: "<<pareja.second<<endl;
}

int primero=1,ultimo=20,mitad=ultimo/2;
vector<int> elegidos;
vector<int> enviados;
vector<double> kresultados(ultimo+1,0);
pair<double,int> pareja;

//Hallando el K-Óptimo
void Optimo(){

  	context ctx;
	socket servidor(ctx,socket_type::rep);
	const string serverconexion = "tcp://*:5001";
	servidor.bind(serverconexion);

	//Eligiendo los K's que necesitamos
	elegidos.push_back(primero);
	elegidos.push_back(mitad);
	elegidos.push_back(ultimo);

	int i=0;
	int op=1;
	int banMensaje=0;
	int divi =8; 
	bool seguir;
	int banderafinal=0;
	while(true){

		mostrarVectores(kresultados,enviados,elegidos);

		string inicio;
		zmqpp::message saludo;
		servidor.receive(saludo);
		saludo >> inicio;
		string resultado, k;
				
		if(inicio == "oe"){
			if(i<elegidos.size()){
				int ksito=elegidos[i];
				string puntoya= to_string(ksito);
				zmqpp::message enviok;
				enviados.push_back(elegidos[i]);
				enviok << puntoya;
				servidor.send(enviok);
				i++;
			}
		}
		else{
			mensajeRec(pareja,banMensaje,k,resultado,inicio);
			cout<<"Push back de: "<<atof(inicio.c_str())<<endl;
			kresultados[pareja.second]=pareja.first;
			int ksito;
			string puntoya;
			bool a=verificar(kresultados,elegidos[i]);
			bool b=verificar2(enviados,elegidos[i]);
			if (a or b){
				if(elegidos[i]+1 != ultimo){
					ksito=elegidos[i+1];
					enviados.push_back(elegidos[i+1]);
					i=i+2;
				}
				else{
					enviados.push_back(elegidos[i]);
				}				
			}
			else{
				ksito=elegidos[i];
				enviados.push_back(elegidos[i]);
				i++;
			}
			if(banderafinal==1){
				puntoya="bye";
				cout <<"El k optimo se encuentra entre el "<<primero<<" y el "<<ultimo<<endl; 
			}	
			else
				puntoya= to_string(ksito);
			zmqpp::message enviok;
			enviok << puntoya;
			servidor.send(enviok);
			
			
		}
		if(enviados[enviados.size()-1] == elegidos[elegidos.size()-1]){
			cout<< "enviado "<<enviados[enviados.size()-1]<<" ele "<<elegidos[elegidos.size()-1]<< endl;
			if (op == 1){
				Repartir(elegidos,enviados,ultimo,divi);
				op=2;	
			}
			else{
				if(verificar(kresultados,ultimo)){
					seguir=evaluar(elegidos,enviados,kresultados,primero,mitad,ultimo,divi);
					if (seguir){
						banderafinal=1;
					}
						
					//divi=divi*2;
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
    mostrarVectores(kresultados,enviados,elegidos);
    cout << "Tiempo: " << tTotal.elapsed() << endl;
}