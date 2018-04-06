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


using namespace std;

class PointUser
{
private:
	int id_point, id_grupo;
	vector<pair<short,short>> values;
	int total_Peliculas;
	bool esCentroide;

public:
	PointUser(int id_point, vector<pair<short,short>>& valores)
	{
		this->id_point = id_point;
		total_Peliculas = valores.size();

		for(int i = 0; i < total_Peliculas; i++)
			this->values.push_back(valores[i]);

		id_grupo = -1;
		esCentroide=false;
	}

	int getID()
	{
		return id_point;
	}

	void setGrupo(int id_grupo)
	{
		this->id_grupo = id_grupo;
	}

	int getGrupo()
	{
		return id_grupo;
	}

	pair<short,short> getPair(int indice)
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

	vector<pair<short,short>> getValues(){
		return values;
	};
};

class Grupo
{
private:
	int id_grupo;
	vector<pair <short,short>> centroide;
	vector<PointUser> points;
	int popo;
	int total_Peliculas;

public:
	Grupo(int id_grupo, PointUser point)
	{
		this->id_grupo = id_grupo;
		this->popo= point.getID();

		this-> total_Peliculas = point.getTotalPeliculas();

		for(int i = 0; i < total_Peliculas; i++)
			centroide.push_back(point.getPair(i));

	}

	void addPoint(PointUser point)
	{
		points.push_back(point);
	}

	bool removePoint(int id_point)
	{
		int total_points = points.size();

		for(int i = 0; i < total_points; i++)
		{
			if(points[i].getID() == id_point)
			{
				points.erase(points.begin() + i);
				return true;
			}
		}
		return false;
	}

	void nuevoCentroide(vector<pair<short,short>>& vectorcito){
		centroide=vectorcito;
	}

	pair <short,short> getCentralPair(int index)
	{
		return centroide[index];
	}

	int getTotal_Peliculas(){
		return total_Peliculas;
	}

	PointUser getPoint(int index)
	{
		return points[index];
	}

	int getTotalPoints()
	{
		return points.size();
	}

	int getID()
	{
		return id_grupo;
	}

	int getPopo()
	{
		return popo;
	}


	vector<pair<short,short>> getCentroide(){
		return centroide;
	};
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

	double ModuloP(PointUser p){

		int resultado=0;
		vector<pair<short,short>> punto;
		punto=p.getValues();
		for(int i=0; i<punto.size();i++){
			resultado+=punto[i].first * punto[i].first;

		}
		double res=sqrt(resultado);
		return res;
	}

	double ModuloG(Grupo g){

		int resultado=0;
		vector<pair<short,short>> grupo;
		grupo=g.getCentroide();
		for(int i=0; i<grupo.size();i++){
			resultado+=grupo[i].first * grupo[i].first;

		}
		double res=sqrt(resultado);
		return res;
	}

	void Ordenar(vector<pair<short,short>>& array, int start,int end){

	    int pivot;

	    if (start < end) {
	        pivot = divide(array, start, end);

	        // Ordeno la lista de los menores
	        Ordenar(array, start, pivot - 1);

	        // Ordeno la lista de los mayores
	        Ordenar(array, pivot + 1, end);
	    }
	}

			// Función para dividir el array y hacer los intercambios
	int divide(vector<pair<short,short>>& array, int start, int end) {
	    int left;
	    int right;
	    short pivot;
	    pair<short,short> temp;

	    pivot = array[start].second;
	    left = start;
	    right = end;

	    // Mientras no se cruzen los índices
	    while (left < right) {
	        while (array[right].second > pivot) {
	            right--;
	        }

	        while ((left < right) && (array[left].second <= pivot)) {
	            left++;
	        }

	        // Si todavía no se cruzan los indices seguimos intercambiando
	        if (left < right) {
	            temp = array[left];
	            array[left] = array[right];
	            array[right] = temp;
	        }
	    }

	    // Los índices ya se han cruzado, ponemos el pivot en el lugar que le corresponde
	    temp = array[right];
	    array[right] = array[start];
	    array[start] = temp;

	    // La nueva posición del pivot
	    return right;
	}

	// Función recursiva para hacer el ordenamiento

	int ProdPunto(PointUser p,Grupo g){

		int resultado=0;
		vector<pair<short,short>> punto,centroide;
		punto=p.getValues();
		centroide=g.getCentroide();


		for(int i=0; i<punto.size();){
			for(int j=0; j<centroide.size();){

				if(punto[i].second == centroide[j].second){
					
					resultado+=punto[i].first * centroide[j].first;
					i++;
					j++;

				}

				else{

					if(punto[i].second < centroide[j].second){
						i++;
						if(i>punto.size()){
							break;
						}
					}
					else{
						j++;
					}
				}
				
				
			}
			i++;
		}
		return resultado;
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


		//Asignando cada punto a un centroide

		int idPert;

		for(int i=0;i < points.size();i++){
			double min_angul = 360;
			for(int j=0;j < Grupos.size();j++){

				//cout << points[i].getID()<< endl;
				//cout << Grupos[j].getPopo()<< endl<<endl;
				int r = ProdPunto(points[i], Grupos[j]);
				double m1 =ModuloP(points[i]);
				double m2 =ModuloG(Grupos[j]);
				float resultado = (r/(m1*m2));
				float arc= acos(resultado) *180 / M_PI;
				if(arc < min_angul){
					min_angul = arc;
					idPert = j;

				}
			}
			points[i].setGrupo(idPert);
			Grupos[idPert].addPoint(points[i]);
		}

		for(int i=0;i < Grupos.size();i++){
			cout << "Grupo # " << i <<endl<<endl;
			for(int j=0;j < Grupos[i].getTotalPoints();j++){
				
				cout<< Grupos[i].getPoint(j).getID()<<endl;

			}
			cout<<endl<<endl;	
		}

		
		int op=0;
		vector<pair<short,short>> VecCentro;

		for(int i=0;i < 5;i++){
			vector<pair<short,short>> VecCentro;
			//Grupos[i].getTotalPoints()
			int l;
			int k=0;
			for(int j=0;j <Grupos[i].getTotalPoints();j++){
			
				if(VecCentro.size()!= 0 and j > 0 ){
					op=VecCentro.size();
					for(int l=0;l < op;){
						//cout << VecCentro[l].second << "   " << Grupos[i].getPoint(j).getPair(k).second<<endl;
						if(VecCentro[l].second == Grupos[i].getPoint(j).getPair(k).second){
							VecCentro[l].first+=Grupos[i].getPoint(j).getPair(k).first;
							k++;
							l++;
						}
						
						if(VecCentro[l].second < Grupos[i].getPoint(j).getPair(k).second){
							l++;
							/*if(VecCentro[op-1].second < Grupos[i].getPoint(j).getPair(k).second){
								VecCentro.push_back(Grupos[i].getPoint(j).getPair(k));
								k++;
							}*/

						}

						if(k >= Grupos[i].getPoint(j).getTotalPeliculas()){
								break;
						}

						if(VecCentro[l].second > Grupos[i].getPoint(j).getPair(k).second)
						{
							VecCentro.push_back(Grupos[i].getPoint(j).getPair(k));
							k++;

						}

						
							

					}
				}

				else{

					for(int n=0;n < Grupos[i].getPoint(j).getTotalPeliculas();n++){
						VecCentro.push_back(Grupos[i].getPoint(j).getPair(n));


						
					}
				}
				
				while(k < Grupos[i].getPoint(j).getTotalPeliculas() and Grupos[i].getPoint(j).getPair(k).second > VecCentro[VecCentro.size()-1].second){
					VecCentro.push_back(Grupos[i].getPoint(j).getPair(k));
					k++;
				}
				k=0;
				Ordenar(VecCentro,0,VecCentro.size()-1);
		
			}
			
			
			for(int i=0;i < VecCentro.size();i++){
				cout <<"Vec "<< "("<< VecCentro[i].first<<","<< VecCentro[i].second<<")"<<"-"<<endl;

			}
			cout<<"-----------------------------------------------------------------"<<endl;
			
		}


		
			
	}
	
};


int LlenarDatos(vector<pair<short,short>>& valores,string linea){
	
	pair<short,short> pareja;
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

int main()
{	
	ifstream archivo_entrada("users.txt");
    string linea;
    vector<PointUser> points;

    while(getline(archivo_entrada, linea)){

    	vector<pair<short,short>> valores;
    	int usuario=LlenarDatos(valores,linea);

    	PointUser p(usuario, valores);
    	//cout<< p.getID() << endl;
    	points.push_back(p);

    }
    cout<<"hola"<<endl;
    KMeans kmeans(5,1000,16);
    kmeans.run(points);
}