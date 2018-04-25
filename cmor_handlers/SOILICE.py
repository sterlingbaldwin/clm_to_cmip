float SOILICE(time, levgrnd, lat, lon) ;
		SOILICE:long_name = "soil ice (vegetated landunits only)" ;
		SOILICE:units = "kg/m2" ;
		SOILICE:cell_methods = "time: mean" ;
		SOILICE:_FillValue = 1.e+36f ;
		SOILICE:missing_value = 1.e+36f ;
		SOILICE:cell_measures = "area: area" ;