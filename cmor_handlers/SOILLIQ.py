float SOILLIQ(time, levgrnd, lat, lon) ;
		SOILLIQ:long_name = "soil liquid water (vegetated landunits only)" ;
		SOILLIQ:units = "kg/m2" ;
		SOILLIQ:cell_methods = "time: mean" ;
		SOILLIQ:_FillValue = 1.e+36f ;
		SOILLIQ:missing_value = 1.e+36f ;
		SOILLIQ:cell_measures = "area: area" ;