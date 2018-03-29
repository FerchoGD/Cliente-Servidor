/* strtok example */
#include <stdio.h>
#include <string.h>
#include <iostream>
#include <fstream>
#include <vector>

using namespace std;

int main ()

{
  //ifstream archivo_entrada("usuarios.txt");

  char * str;
  char * pch;

  while(getline(archivo_entrada, str)){
	  pch = strtok (str," [](),.-");
	  while (pch != NULL)
	  {
	    cout<<pch<<endl;
	    pch = strtok (NULL, " [](),.-");
	  }
	}
  return 0;
}


/*

int main(){

	ifstream archivo_entrada("usuarios.txt");
	    
		char  linea[]="";
	    while(getline(archivo_entrada, linea)) {
	            
		  char * caracter;

		 
		  caracter = strtok (linea," ,[]()");
		  while (caracter != NULL)
		  {
		    cout<<caracter<<endl;
		    caracter = strtok (NULL, " ,[]()");
		  }
	    }
}

*/