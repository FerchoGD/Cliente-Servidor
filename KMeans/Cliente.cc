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

class PointUser
{
private:
	int id_point, id_grupo;
	vector<pair<double,double>> values;
	int total_Peliculas;
	bool esCentroide;
	double modulo=0;
	double min_angul=360;

public:
	PointUser(int id_point, vector<pair<double,double>>& valores)
	{
		this->id_point = id_point;
		total_Peliculas = valores.size();
		int resultado=0;
		for(int i = 0; i < total_Peliculas; i++){
			this->values.push_back(valores[i]);
			resultado+=values[i].first * values[i].first;
		}
		modulo=sqrt(resultado);
		id_grupo = -1;
		esCentroide=false;
	}

	int getID()
	{
		return id_point;
	}
	double getModulo()
	{
		return modulo;
	}

	void setGrupo(int id_grupo)
	{
		this->id_grupo = id_grupo;
	}


	int getGrupo()
	{
		return id_grupo;
	}

	void setNuevo_angulo(double nuevo_angul)
	{
		this->min_angul = nuevo_angul;
	}


	int getAngulo()
	{
		return min_angul;
	}

	pair<double,double> getPair(int indice)
	{
		return values[indice];
	}

	int getTotalPeliculas()
	{
		return total_Peliculas;
	}

	void setCentroide(){
		this->esCentroide=true;
	}

	bool getCentroide(){
		return esCentroide;
	}

	vector<pair<double,double>> getValues(){
		return values;
	}
};

class Grupo
{
private:
	int id_grupo;
	vector<double> centroide;
	vector<PointUser> points;
	int total_Peliculas;
	double modulo=0;
	int idpGrupo;
	double errorMin=0;
	double errorMinPre=0;

public:
	Grupo(int id_grupo, PointUser point)
	{
		this->id_grupo = id_grupo;
		this-> total_Peliculas = point.getTotalPeliculas();
		idpGrupo=point.getID();
		for(int i=0; i< 17771; i++){
			centroide.push_back(0);
		}
		for(int i = 0; i < total_Peliculas; i++)
			centroide[point.getPair(i).second]=point.getPair(i).first;


		modulo=point.getModulo();

	}
	void nuevoCentroide(vector<double> &vectorcito){
		double resultado=0;
		centroide=vectorcito;
		for (int i=0; i < 17771; i++){
			//cout<<centroide[i]<<" <-> "<<vectorcito[i]<<endl;
			//cout<<i<<"-- "<<centroide[i]<<endl;	
			resultado+=centroide[i] * centroide[i];
		}

		modulo=sqrt(resultado);
	}

	void addPoint(PointUser point)
	{
		points.push_back(point);
	}

	void Error(double min_a)
	{	
		errorMin+=min_a;

	}

	void ErrorPre()
	{	
		errorMinPre=errorMin;

	}

	void ErrorCero()
	{	
		errorMin=0;

	}
	void ErrorDiv()
	{	
		if(points.size()==0)
			errorMin=errorMin;
		else
			errorMin=errorMin/points.size();

	}

	double getErrorPre()
	{
		return errorMinPre;
	}

	int getidpGrupo()
	{
		return idpGrupo;
	}

	double getError()
	{
		return errorMin;
	}

	bool Limpiar()
	{
		points.clear();
		return true;
	}

	int getTotal_Peliculas(){
		return total_Peliculas;
	}

	PointUser getPoint(int index)
	{
		return points[index];
	}

	double getModulo()
	{
		return modulo;
	}

	int getTotalPoints()
	{
		return points.size();
	}

	int getID()
	{
		return id_grupo;
	}

	double getCentroideValue(int index){
		return centroide[index];
	}
	vector<double> getCentroide(){
		return centroide;
	}
};

class KMeans
{
private:
	int K; 
	int total_Peliculas;
	vector<Grupo> Grupos;
	int total_Usuarios;

public:
	KMeans(int K, int total_Peliculas, int total_Usuarios)
	{
		this->K = K;
		this->total_Peliculas = total_Peliculas;
		this->total_Usuarios = total_Usuarios;
	}

	int ProdPunto(vector<pair<double,double>> &&vp,vector<double> &&vg){

		int resultado=0;
		for(int i=0; i<vp.size();i++){
					//cout <<"Pelicula " << punto[i].second <<endl;
					//cout <<"Raiting " << punto[i].first<< "  "<< centroide[punto[i].second]<< endl;					
					resultado+=vp[i].first * vg[vp[i].second];
					//cout<<" resultado  "<< resultado<< endl;
				}
					//cout<<" resultado  "<< resultado<< endl<< endl;
		return resultado;
	}

	void PromediarCambiar(vector<double>& centro,Grupo& grupo){
		int numero=grupo.getTotalPoints();
		for(int i=0; i<17771;i++){
			centro[i]= centro[i]/numero;
		}
		grupo.nuevoCentroide(centro);
	}

	double run(vector<PointUser>& points)
	{
		if(K > total_Usuarios or K==0)
			return 0;
		for(int i = 0; i < K; i++)
		{
			while(true)				
			{
				int index_point = rand() % total_Usuarios;
				if(!points[index_point].getCentroide())
				{
					points[index_point].setGrupo(i);
					points[index_point].setCentroide();
					Grupo grupo(i, points[index_point]);
					Grupos.push_back(grupo);
					break;
				}
			}
		}

		int iter=1;
		int control=0;
		while(true)
		{
		//Asignando cada punto a un centroide
			int idPert;
			cout<<"Iteracion #"<<iter<<endl;
			//cout << "Inicio ProdPunto" << endl;
			Timer t;
			#pragma omp parallel for
			for(int i=0;i < Grupos.size();i++){
				double m2 = Grupos[i].getModulo();				
				for(int j=0;j < points.size() ;j++){
					double m1 = points[j].getModulo();

					//cout << points[i].getID()<< endl;
					//cout << Grupos[j].getidpGrupo()<< endl;
					//cout<<"======================="<<endl;
					int r = ProdPunto(points[j].getValues(), Grupos[i].getCentroide());
					//cout<< r << endl;
					double resultado = (r/(m1*m2));
					double arc= acos(resultado) *180 / M_PI;
					if(arc < points[j].getAngulo()){
						points[j].setNuevo_angulo(arc);
						points[j].setGrupo(i);
					}
					//cout <<"Min Ang" << arc << endl<<endl;
				}
				//cout <<"Min Ang" << min_angul << endl;
				//cout << Grupos[idPert].getError()<<endl;
				//cout << " grupo centroide  "<< Grupos[idPert].getidpGrupo() <<endl;
			}
			//cout << "Tiempo: " << t.elapsed() << endl;

			//cout << "Fin ProdPunto" << endl<<endl;
			//cout << "Inicio Calculo error" << endl;
			for(int j=0;j < points.size() ;j++){
				int op = points[j].getGrupo();
				//cout<<"OP es: "<<op<<" ,K es: "<<K<<endl;
				Grupos[op].addPoint(points[j]);
				Grupos[op].Error(points[j].getAngulo());
			}
			//cout << "Fin Calculo error" << endl<<endl;
			
			//cout << "Inicio Nuevo centroide" << endl;
			
			for(int i=0;i < Grupos.size();i++){
				vector<double> VecCentro(17771,0);
				//Timer ts;
				//Grupos[i].getTotalPoints()
				#pragma omp parallel for
				for(int j=0;j < Grupos[i].getTotalPoints();j++){
					
					for(int k=0; k < Grupos[i].getPoint(j).getTotalPeliculas() ; k++ ){
						VecCentro[Grupos[i].getPoint(j).getPair(k).second]+=Grupos[i].getPoint(j).getPair(k).first;
					}
				}
				//cout <<"Cantidad de puntos "<< Grupos[i].getTotalPoints()<<endl;
				//cout << "Tiempo: " << ts.elapsed() << endl;	
				for(int m=0; m<17771;m++){
					VecCentro[m]= VecCentro[m]/Grupos[i].getTotalPoints();
				}

				Grupos[i].nuevoCentroide(VecCentro);
				
			}

			
			//cout << "Fin Nuevo centroide" << endl;
			int hol=0;
			for(int indice=0;indice < Grupos.size(); indice++){
				Grupos[indice].ErrorDiv();
				if(control==1){
					//cout << "Error pre  "<< Grupos[indice].getErrorPre() << "  Error Act  "<< Grupos[indice].getError()<<endl;
					if(Grupos[indice].getErrorPre()-Grupos[indice].getError() < 2){
						hol++;
					}
				}
				Grupos[indice].ErrorPre();
				Grupos[indice].Limpiar();
				Grupos[indice].ErrorCero();
			}
			
			cout << hol <<endl;
			if(hol >= K-1){
				double error=0;
				for(int indice=0; indice<Grupos.size(); indice++){

					error+=Grupos[indice].getErrorPre();
				}
				return error/Grupos.size();
			}
			control=1;
			iter++;

		}

			
	}
	
};


int LlenarDatos(vector<pair<double,double>>& valores,string linea){
	
	pair<double,double> pareja;
    int i=0;

    string usuario, raiting, pelicula;
    for(i;i<linea.size();i++){
    	if(linea[i]==' '){
    		break;
    	}
    	else{
    		usuario+= linea[i];
    	}
    }

    for(i; i<linea.size();){
    	if(linea[i] == ' ' and linea[i+1] == '[' and linea[i+2] == '('){
    		i=i+3;
    		raiting=linea[i];
    		i++;
    	}
    	if(linea[i] == ',' and linea[i+1] == ' ' and linea[i+2] != '('){
    		i=i+2;
    		pelicula=linea[i];
    		i=i+1;
    	}
    	if(linea[i] == ')'){
    		int r=atoi(raiting.c_str());
    		int p=atoi(pelicula.c_str());
    		pareja=make_pair(r,p);
    		valores.push_back(pareja);
    		i=i+4;
    		raiting=linea[i];
    		i=i+1;
    	}
    	else{
    		pelicula+=linea[i];
    		i++;
    	}	
    	

    }	

    int u=atoi(usuario.c_str());
    return u;

    //for(int i=0;i< valores.size();i++){
    //	cout << valores[i].first << endl << valores[i].second << endl;
    //}
}

int main(){
	srand(time(NULL)); 
    string ipserver="localhost"; //Momentaneamente

  	context ctx;
  	//socket socket_out(ctx,socket_type::rep);
  	socket socket_out(ctx,socket_type::req);

	//Conexion Server

	const string conexionserver = "tcp://"+ipserver+":5001";


	socket_out.connect(conexionserver);

	string saludo="oe";
	zmqpp::message iniciando;
	iniciando << saludo;
	cout<<"Saludando"<<endl;
	socket_out.send(iniciando);
	
	while(true){

		ifstream archivo_entrada("users.txt");
	    string linea;
	    vector<PointUser> points;
	    while(getline(archivo_entrada, linea)){
	    	vector<pair<double,double>> valores;
	    	int usuario=LlenarDatos(valores,linea);
	    	PointUser p(usuario, valores);
	    	points.push_back(p);
    	}

		string recibido;
		zmqpp::message msg;
		socket_out.receive(msg);
		msg >> recibido;
		cout<<"El k recibido es: ----------->"<<recibido<<endl<<endl;
		string result;

		if(recibido != "bye"){

			Timer tss;
			KMeans kmeans(atoi(recibido.c_str()),4499,404546);
			result=to_string(kmeans.run(points));
			cout<<endl;
			cout << "Tiempo global: " << tss.elapsed() << endl;
		}
		else
			break;
		string resultado = result +"-"+ recibido.c_str()+" ";
		zmqpp::message mensaje;
		mensaje << resultado ;
		cout<<"resultado: "<<resultado<<endl<<endl;
	    socket_out.send(mensaje);

	    //zmqpp::message bye;
	    //socket_out.receive(bye);
	}
}