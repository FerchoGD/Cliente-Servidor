for(int i=0;i<valores.size();i++){
    		cout << p.getPair(i).first << "  ";
    		cout << p.getPair(i).second << endl;
    		
    	}



int ProdPunto(PointUser p,Grupo g){

	int resultado=0;
	vector<pair<short,short>> punto,centroide;
	punto=p.getValues();
	centroide=g.getCentroide();
	for(int i=0; i<punto.size();){
		for(int j=0; j<centroide.size();){

			if(punto[i].second == centroide[j].second){
				
				resultado+=punto[i].first * centroide[j].first;

			}

			else{

				if(punto[i].second < centroide[j].second){
					i++;
				}
				else{
					j++;
				}
			}
		}
	}
	return resultado;
	}



		int r=ProdPunto(points[0], Grupos[0]);
		cout<<r<<endl;
