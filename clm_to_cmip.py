import os, sys
import argparse
import cmor
import cdms2

from multiprocessing import Pool
from threading import Event
from importlib import import_module
#
# Convert CLM and CAM fields to MIP-like fields
#
#######################################################################################################################################################
# 
# CLM fields
#
#CMIP5 name   standard_name                                                      units       #  CLM fields needed    Derivation
#-----------  -----------------------------------------------------------------  ----------- -  -------------------  ----------------------------------
#burntArea    area_fraction                                                      %           1  ANN_FAREA_BURNED     ANN_FAREA_BURNED*(100/12), or
#                                                                                               FAREA_BURNED         FAREA_BURNED scaled by month
#cCwd         wood_debris_carbon_content                                         kg m-2      1  CWDC                 CWDC/1000
#cLeaf        leaf_carbon_content                                                kg m-2      1  LEAFC                LEAFC/1000
#cLitter      litter_carbon_content                                              kg m-2      1  TOTLITC              TOTLITC/1000
#cMisc        miscellaneous_living_matter_carbon_content                         kg m-2      1  STORVEGC             STORVEGC/1000
#cProduct     carbon_content_of_products_of_anthropogenic_land_use_change        kg m-2      1  TOTPRODC             TOTPRODC/1000
#cRoot        root_carbon_content                                                kg m-2      3  FROOTC               FROOTC+LIVE_ROOTC+DEAD_ROOTC
#                                                                                               LIVE_ROOTC           /1000
#                                                                                               DEAD_ROOTC
#cSoilFast    fast_soil_pool_carbon_content                                      kg m-2      1  SOIL1C               SOIL1C/1000
#cSoilMedium  medium_soil_pool_carbon_content                                    kg m-2      1  SOIL2C               SOIL2C/1000
#cSoilSlow    slow_soil_pool_carbon_content                                      kg m-2      1  SOIL3C               SOIL3C/1000
#cSoil        soil_carbon_content                                                kg m-2      1  TOTSOMC              TOTSOMC/1000
#cVeg         vegetation_carbon_content                                          kg m-2      1  TOTVEGC              TOTVEGC/1000
#cWood        wood_carbon_content                                                kg m-2      1  WOODC                WOODC/1000
#evspsblsoi   water_evaporation_flux_from_soil                                   kg m-2 s-1  1  QSOIL                QSOIL no change
#evspsblveg   water_evaporation_flux_from_canopy                                 kg m-2 s-1  1  QVEGE                QVEGE no change
#fFire        surface_upward_mass_flux_of_carbon_dioxide_expressed_as_           kg m-2 s-1  1  COL_FIRE_CLOSS       COL_FIRE_CLOSS/1000
#             carbon_due_to_emission_from_fires_excluding_anthropogenic_
#             land_use_change
#fLitterSoil  carbon_mass_flux_into_soil_from_litter                             kg m-2 s-1  3  LITR1C_TO_SOIL1C     LITR1C_TO_SOIL1C+LITR2C_TO_SOIL2C
#                                                                                               LITR2C_TO_SOIL2C     +LITR3C_TO_SOIL3C
#                                                                                               LITR3C_TO_SOIL3C     /1000
#fLuc         surface_net_upward_mass_flux_of_carbon_dioxide_expressed_as_       kg m-2 s-1  1  LAND_USE_FLUX        LAND_USE_FLUX/1000
#             carbon_due_to_emission_from_anthropogenic_land_use_change
#fVegLitter   litter_carbon_flux                                                 kg m-2 s-1  1  LITFALL              LITFALL/1000
#gpp          gross_primary_productivity_of_carbon                               kg m-2 s-1  1  GPP                  GPP/1000
#hfdsn        surface_downward_heat_flux_in_snow                                 W m-2       1  FGR                  FGR reverse sign
#lai          leaf_area_index                                                    1           1  TLAI                 TLAI no change
#lwsnl        liquid_water_content_of_snow_layer                                 kg m-2      1  SNOWLIQ              SNOWLIQ no change
#mrfso        soil_frozen_water_content                                          kg m-2      1  SOILICE              SOILICE summed over all layers,
#                                                                                                                    capped over icy regions at 5000
#mrlsl        moisture_content_of_soil_layer                                     kg m-2      2  SOILLIQ              SOILLIQ+SOILICE summed,
#                                                                                               SOILICE              at each soil depth
#mrro         runoff_flux                                                        kg m-2 s-1  1  QRUNOFF              QRUNOFF no change
#mrros        surface_runoff_flux                                                kg m-2 s-1  1  QOVER                QOVER no change
#mrsos        moisture_content_of_soil_layer                                     kg m-2      1  SOILWATER_10CM       SOILWATER_10CM no change
#mrso         soil_moisture_content                                              kg m-2      2  SOILICE              SOILICE+SOILLIQ, summed over Z,
#                                                                                               SOILLIQ              capped over icy regions at 5000
#nbp          surface_net_downward_mass_flux_of_carbon_dioxide_expressed_as_
#             carbon_due_to_all_land_processes                                   kg m-2 s-1  1  NBP                  NBP/1000
#nppLeaf      net_primary_productivity_of_carbon_accumulated_in_leaves           kg m-2 s-1  1  LEAFC_ALLOC          LEAFC_ALLOC/1000
#npp          net_primary_productivity_of_carbon                                 kg m-2 s-1  1  NPP                  NPP/1000
#nppRoot      net_primary_productivity_of_carbon_accumulated_in_roots            kg m-2 s-1  1  FROOTC_ALLOC         FROOTC_ALLOC/1000
#nppWood      net_primary_productivity_of_carbon_accumulated_in_wood             kg m-2 s-1  1  WOODC_ALLOC          WOODC_ALLOC/1000
#prveg        precipitation_flux_onto_canopy                                     kg m-2 s-1  1  QINTR                QINTR no change
#ra           plant_respiration_carbon_flux                                      kg m-2 s-1  1  AR                   AR/1000
#rGrowth      surface_upward_carbon_mass_flux_due_to_plant_respiration_for_      kg m-2 s-1  1  GR                   GR/1000
#             biomass_growth
#rh           heterotrophic_respiration_carbon_flux                              kg m-2 s-1  1  HR                   HR/1000
#rMaint       surface_upward_carbon_mass_flux_due_to_plant_respiration_for_      kg m-2 s-1  1  MR                   MR/1000
#             biomass_maintenance
#snc          surface_snow_area_fraction                                         %           1  FSNO                 FSNO*100
#snd          surface_snow_thickness                                             m           1  SNOWDP               SNOWDP no change
#snm          surface_snow_melt_flux                                             kg m-2 s-1  1  QMELT                QMELT no change 
#snw          surface_snow_amount                                                kg m-2      1  H2OSNO               H2OSNO no change 
#sootsn       soot_content_of_surface_snow                                       kg m-2      3  SNOBCMSL             SNOBCMSL+SNODSTMSL+SNOOCMSL
#                                                                                               SNODSTMSL 
#                                                                                               SNOOCMSL
#tran         transpiration_flux                                                 kg m-2 s-1  1  QVEGT                QVEGT no change
#tsl          soil_temperature                                                   K           1  TSOI                 TSOI no change
#sfcWind      wind_speed                                                         m s-1       1  WIND                 WIND no change
#
#######################################################################################################################################################
#
# Available CMIP5 "Amon" fields from CLM equivalents
#
#evspsbl      water_evaporation_flux                                             kg m-2 s-1  3  QSOIL                QSOIL+QVEGE+QVEGT
#                                                                                               QVEGE
#                                                                                               QVEGE
#hfls         surface_upward_latent_heat_flux                                    W m-2       1  EFLX_LH_TOT          EFLX_LH_TOT no change or
#                                                                                            3  FCTR                 FCTR + FCEV + FGEV
#                                                                                               FCEV
#                                                                                               FGEV
#hfss         surface_upward_sensible_heat_flux                                  W m-2       1  FSH                  FSH no change
#hurs         relative_humidity                                                  %           1  RH2M                 RH2M no change
#huss         specific_humidity                                                  1           1  Q2M                  Q2M no change
#pr           precipitation_flux                                                 kg m-2 s-1  1  RAIN+SNOW            RAIN+SNOW (same numerical value)
#prsn         snowfall_flux                                                      kg m-2 s-1  1  SNOW                 SNOW (same numerical value)
#ps           surface_air_pressure                                               Pa          1  PBOT                 PBOT no change
#rlds         surface_downwelling_longwave_flux_in_air                           W m-2       1  FLDS                 FLDS no change
#rlus         surface_upwelling_longwave_flux_in_air                             W m-2       1  FIRE                 FIRE no change
#rsds         surface_downwelling_shortwave_flux_in_air                          W m-2       1  FSDS                 FSDS no change
#rsus         surface_upwelling_shortwave_flux_in_air                            W m-2       1  FSR                  FSR no change
#tas          air_temperature                                                    K           1  TSA                  TSA no change
#
####

class Cmorizer(object):
    """
    A utility class to cmorize clm time series files
    """
    def __init__(self, var_list, input_path, output_path, caseid, nproc=6, handlers='./cmor_handlers'):
        self._var_list = var_list
        self._input_path = input_path
        self._output_path = output_path
        self._nproc = nproc
        self._handlers_path = handlers
        self._caseid = caseid
        self._event = Event()
        self._pool = None
        self._pool_res = None
    
    def run(self):
        handlers = os.listdir(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                self._handlers_path))
        self._handlers = list()
        for handler in handlers:
            if not handler.endswith('.py'):
                continue
            if handler == "__init__.py":
                continue

            module, _ = handler.rsplit('.', 1)
            if module not in self._var_list:
                continue
            module_path = '.'.join([self._handlers_path, module])
            mod = import_module(module_path)
            met = getattr(mod, 'handle')
            self._handlers.append({module: met})
        
        print '--- printing handlers ---'
        for handler in self._handlers:
            for key, val in handler.items():
                print '\t' + val()

        print '\n--- calling handlers ---'
        print '--- running with {} processes ---'.format(self._nproc)
        self._pool = Pool(self._nproc)
        self._pool_res = list()

        for handler in self._handlers:
            for key, val in handler.items():
                kwds = {
                    'infile': os.path.join(
                                self._input_path, 
                                self._caseid + '.' + key + '.nc'),
                    'tables_dir': self._handlers_path
                }
                self._pool_res.append(
                    self._pool.apply_async(val, args=(), kwds=kwds))
        
        for res in self._pool_res:
            print res.get()
    
    def worker_wrapper(self, func, args):
        return func(**args)
    
    def terminate(self):
        if self._pool:
            self._pool.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--var-list',
        nargs='+', required=True,
        help='space seperated list of variables to convert from clm to cmip')
    parser.add_argument(
        '-c', '--caseid',
        required=True,
        help='name of case e.g. 20180129.DECKv1b_piControl.ne30_oEC.edison')
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='path to directory containing clm data with single variables per file')
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='where to store cmorized outputoutput')
    parser.add_argument(
        '-n', '--num-proc',
        default=6, type=int,
        help='optional: number of processes, default = 6')
    parser.add_argument(
        '-H', '--handlers',
        default='cmor_handlers',
        help='optional: path to cmor handlers directory, default = ./cmor_handlers')
    try:
        args = parser.parse_args(sys.argv[1:])
    except:
        parser.print_help()
        sys.exit(1)
    
    cmorizer = Cmorizer(
        var_list=args.var_list,
        input_path=args.input,
        output_path=args.output,
        caseid=args.caseid,
        nproc=args.num_proc,
        handlers=args.handlers)
    try:
        cmorizer.run()
    except KeyboardInterrupt as e:
        print '--- caught keyboard kill event ---'
        cmorizer.terminate()
    