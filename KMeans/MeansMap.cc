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
#include <time.h>
#include <map>

using namespace std;

class PointUser
{
private:
	int id_point, id_grupo, prev_grupo;
	map<int,double> values;
	int total_Peliculas;
	bool esCentroide;
	double modulo=0;

public:
	PointUser(int id_point, map<int,double>& valores)
	{
		this->id_point = id_point;
		total_Peliculas = valores.size();
		int resultado=0;

		for (map<int,double>::iterator it=valores.begin(); it!=valores.end(); it++){
			values[it->first]=it->second;
    		cout << it->first << " => " << it->second << '\n';
    		resultado+=it->second;
		}

		modulo=sqrt(resultado);
		prev_grupo= -1;
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

	void setPrevGrupo(int id)
	{
		this->prev_grupo = id;
	}

	int getGrupo()
	{
		return id_grupo;
	}

	int getPrevGrupo()
	{
		return prev_grupo;
	}

	int getRaiting(int indice)
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

	map<int,double> getValues(){
		return values;
	}
};



class Grupo
{
private:
	int id_grupo;
	map<int,double> centroide;
	vector<PointUser> points;
	int total_Peliculas;
	double modulo=0;
	int popo;

public:
	Grupo(int id_grupo, PointUser point)
	{
		this->id_grupo = id_grupo;
		this-> total_Peliculas = point.getTotalPeliculas();
		popo=point.getID();

		for(int i=0; i< 17771; i++){
			centroide[i]=0.0;
		}


		for (map<int,double>::iterator it=point.getValues().begin(); it!=point.getValues().end(); it++){
			centroide[it->first]=it->second;
    		cout << it->first << " => " << centroide[it->first] << '\n';
		}

		modulo=point.getModulo();

	}

	void addPoint(PointUser point)
	{
		points.push_back(point);
	}

	int getPopo()
	{
		return popo;
	}

	bool Limpiar()
	{
		/*for (int i=0; i < points.size(); i++)
			cout << points[i].getID() << endl;
			cout << "----------------------------------"<< endl;*/
		points.clear();
		
		return true;
	}

	void nuevoCentroide(map<int,double> vectorcito){
		for (int i=0; i < 17771; i++)
			centroide[i]=0;

		double resultado=0;
		for (int i=0; i < 17771; i++){
			//cout<<centroide[i]<<" <-> "<<vectorcito[i]<<endl;
			centroide[i]=vectorcito[i];
			//cout<<i<<"-- "<<centroide[i]<<endl;	
			resultado+=centroide[i] * centroide[i];
		}

		modulo=sqrt(resultado);

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

	map<int,double> getCentroide(){
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


	int ProdPunto(PointUser p,Grupo g){

		int resultado=0;
		map<int,double> punto;
		map<int,double> centroide;
		punto=p.getValues();
		centroide=g.getCentroide();

		for (map<int,double>::iterator it=punto.begin(); it!=punto.end(); it++){
			if(centroide.find( it->first ) != centroide.end()){
	    		//cout << it->first << " <=> "<< it->second <<" * "<<centroide[it->first] <<'\n';
	    		resultado+= it->second * centroide[it->first];
	    	}
		}


		cout<<" Resultado  "<< resultado<< endl<< endl;
		return resultado;
	}


	void PromediarCambiar(map<int,double>& centro,Grupo& grupo){
		int numero=grupo.getTotalPoints();
		for(int i=0; i<17771;i++){
			centro[i]= centro[i]/numero;
		}
		grupo.nuevoCentroide(centro);
	}



	void run(vector<PointUser>& points)
	{
		if(K > total_Usuarios)
			return;

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


		while(true)
		{

		//Asignando cada punto a un centroide


			int idPert;


			cout<<"Iteracion #"<<iter<<endl<<endl;
 
			cout << "Inicio ProdPunto" << endl;
			for(int i=0;i < points.size();i++){
				
				points[i].setPrevGrupo(points[i].getGrupo());
				double min_angul = 360;
				for(int j=0;j < Grupos.size();j++){

					
					//cout << points[i].getID()<< endl;
					//cout << Grupos[j].getPopo()<< endl;
					//cout<<"======================="<<endl;
					int r = ProdPunto(points[i], Grupos[j]);
					double m1 = points[i].getModulo();
					double m2 = Grupos[j].getModulo();
					float resultado = (r/(m1*m2));
					float arc= acos(resultado) *180 / M_PI;
					if(arc < min_angul){
						min_angul = arc;
						idPert = j;

					}

					//cout <<"Min Ang" << arc << endl<<endl;
				}
				points[i].setGrupo(idPert);
				Grupos[idPert].addPoint(points[i]);
			}

			cout << "Fin ProdPunto" << endl;

			/*for(int i=0;i < Grupos.size();i++){
				cout << "Grupo # " << i <<endl<<endl;
				for(int j=0;j < Grupos[i].getTotalPoints();j++){
						
					//cout<< Grupos[i].getPoint(j).getID()<<endl;

				}

				cout<<endl<<endl;	
			}*/

			cout << "Inicio Nuevo centroide" << endl;
			int op=0;
			map<int,double> VecCentro;

			for(int i=0;i < Grupos.size();i++){
				map<int,double> VecCentro;
				for(int a=0; a<= 17771; a++){
					VecCentro[a]=0.0;
				}

				//Grupos[i].getTotalPoints()
				for(int j=0;j < Grupos[i].getTotalPoints();j++){
					for (map<int,double>::iterator it=Grupos[i].getPoint(j).getValues().begin(); it!=Grupos[i].getPoint(j).getValues().end(); it++){
						VecCentro[it->first]=it->second;					}
				}
				
				PromediarCambiar(VecCentro,Grupos[i]);				
			}


			cout << "Fin Nuevo centroide" << endl;
	
			for(int indice=0;indice < Grupos.size(); indice++){
				Grupos[indice].Limpiar();

			}
			
			bool sigo=false;
			for(int i=0; i< points.size(); i++){
				if(points[i].getGrupo() != points[i].getPrevGrupo()){
					sigo=true;
				}
			}

			if(!sigo)
				break;

			iter++;



		}

			
	}
	
};


int LlenarDatos(map<int,double>& valores,string linea){
	
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
    		double r=atoi(raiting.c_str())/1.0;
    		int p=atoi(pelicula.c_str());
    		valores[p]=r;
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

int main()
{	
	srand(time(NULL)); 
	ifstream archivo_entrada("usuarios.txt");
    string linea;
    vector<PointUser> points;

    while(getline(archivo_entrada, linea)){

    	map<int,double> valores;
    	int usuario=LlenarDatos(valores,linea);

    	PointUser p(usuario, valores);
    	//cout<< p.getID() << endl;
    	points.push_back(p);

    }

    cout<<"hola"<<endl;
    KMeans kmeans(5,17771,20);
    kmeans.run(points);
}