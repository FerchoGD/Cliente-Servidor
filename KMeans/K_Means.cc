#include <iostream>
#include <cstdlib>
#include <fstream>
#include <string>
#include <string.h>
#include <vector>
#include <tuple>

using namespace std;


void LlenarDatos(vector<tuple<int, vector <tuple<int,int>>>>& datos){

	ifstream archivo_entrada("usuarios.txt");
	tuple<int,int> calificacion;
	tuple<int,tuple<int,int>> user;

    string linea;

    getline(archivo_entrada, linea);

    string delimiter1 = "[(";

	size_t pos1 = 0;
	string token1;
	while ((pos1 = linea.find(delimiter1)) != string::npos) {
	    token1 = linea.substr(0, pos1);
	    cout << token1 << endl;
	    linea.erase(0, pos1 + delimiter1.length());
	    //linea.erase(0, pos + delimiter.length()+2);
	}
	cout<<token1;
	//cout << linea;
	cout << endl<< endl;
    
    /*
	string delimiter = "),";

	size_t pos = 0;
	size_t opc;
	string token;
	while ((pos = linea.find(delimiter)) != string::npos) {
	    token = linea.substr(0, pos);
	    cout << token << endl;
	    
	   
	    string res= to_string(token[3]) + to_string(token[4]) + to_string(token[5]) + to_string(token[6]);
	    cout << res <<endl;

	    linea.erase(0, pos + delimiter.length()+2);
	    //linea.erase(0, pos + delimiter.length()+2);
	}
	//cout << linea;
	*/
		                

}

int main()
{

        vector<tuple<int, vector<tuple<int,int>>>> vectorsito;
        LlenarDatos(vectorsito);
        
        for(int i=0; i<vectorsito.size(); i++){
        	cout<< std::get<0>(vectorsito[i])<<endl;
        }
    
        return 0;
}