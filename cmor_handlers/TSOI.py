float TSOI(time, levgrnd, lat, lon) ;
		TSOI:long_name = "soil temperature (vegetated landunits only)" ;
		TSOI:units = "K" ;
		TSOI:cell_methods = "time: mean" ;
		TSOI:_FillValue = 1.e+36f ;
		TSOI:missing_value = 1.e+36f ;
		TSOI:cell_measures = "area: area" ;