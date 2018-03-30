#include <iostream>
#include <cstdlib>
#include <fstream>
#include <string>
#include <utility>
#include <string.h>
#include <vector>
#include <tuple>
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

		points.push_back(point);
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
};

class KMeans
{
private:
	int K; 
	int total_Peliculas;
	vector<Grupo> Grupos;
	int total_Usuarios;

	// return ID of nearest center (uses euclidean distance)
	/*
	int getIDNearestCenter(Point point)
	{
		double sum = 0.0, min_dist;
		int id_grupo_center = 0;

		for(int i = 0; i < total_values; i++)
		{
			sum += pow(grupos[0].getCentralValue(i) -
					   point.getValue(i), 2.0);
		}

		min_dist = sqrt(sum);

		for(int i = 1; i < K; i++)
		{
			double dist;
			sum = 0.0;

			for(int j = 0; j < total_values; j++)
			{
				sum += pow(grupos[i].getCentralValue(j) -
						   point.getValue(j), 2.0);
			}

			dist = sqrt(sum);

			if(dist < min_dist)
			{
				min_dist = dist;
				id_grupo_center = i;
			}
		}

		return id_grupo_center;
	}
*/
public:
	KMeans(int K, int total_Peliculas, int total_Usuarios)
	{
		this->K = K;
		this->total_Peliculas = total_Peliculas;
		this->total_Usuarios = total_Usuarios;
	}

	void run(vector<PointUser>& points)
	{
		if(K > total_Usuarios)
			return;

		// choose K distinct values for the centers of the clusters
		for(int i = 0; i < K; i++)
		{
			while(true)
			{
				int index_point = rand() % total_Usuarios;

				if(!points[index_point].getCentroide())
				{
					points[index_point].setGrupo(i);
					Grupo grupo(i, points[index_point]);
					Grupos.push_back(grupo);
					break;
				}
			}
		}


		while (true){

			for(int i=0; i<Grupos.size();i++){
				cout<< Grupos[i].getPopo()<<endl;
				for(int j=0;j<Grupos[i].getTotal_Peliculas();j++){
					cout << Grupos[i].getCentralPair(j).first << " " << Grupos[i].getCentralPair(j).second<< endl;
					

				}
			}
			break;

			//Asignar cada punto en un grupo
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
	ifstream archivo_entrada("usuarios.txt");
    string linea;
    vector<PointUser> points;

    while(getline(archivo_entrada, linea)){

    	vector<pair<short,short>> valores;
    	int usuario=LlenarDatos(valores,linea);

    	PointUser p(usuario, valores);
    	//cout<< p.getID() << endl;
    	points.push_back(p);

    }
    KMeans kmeans(5,1000,20);
    kmeans.run(points);
}