import os
import cdms2
import cmor

def handle(infile="", tables_dir=""):
    """
    Transform E3SM.TS to CMIP6.ts
    """
    if not infile:
        return "hello from {}".format(__name__)
    
    # extract data
    f = cdms2.open(infile)
    data = f('TS')
    lat = data.getLatitude()[:]
    lon = data.getLongitude()[:]
    lat_bnds = f('lat_bnds')
    lon_bnds = f('lon_bnds')
    time = data.getTime()
    climatology_bnds = f('climatology_bounds')
    f.close()

    # setup cmor
    tables_path = os.path.join(tables_dir, 'Tables')
    test_path = os.path.join(tables_dir, 'Test', 'common_user_input.json')
    cmor.setup(inpath=tables_path, netcdf_file_action=cmor.CMOR_REPLACE)
    cmor.dataset_json(test_path)
    table = 'CMIP6_Amon.json'
    cmor.load_table(table)

    # set the axes
    axes = [{
        'table_entry': 'time',
        'units': time.units
    }, {
        'table_entry': 'latitude',
        'units': 'degrees_north',
        'coord_vals': lat[:],
        'cell_bounds': lat_bnds[:]
    }, {
        'table_entry': 'longitude',
        'units': 'degrees_east',
        'coord_vals': lon[:],
        'cell_bounds': lon_bnds[:]
    }]
    axis_ids = list()
    for axis in axes:
        axis_id = cmor.axis(**axis)
        axis_ids.append(axis_id)

    # setup the cmor variable
    varid = cmor.variable('ts', 'K', axis_ids)

    # write the data out
    for index, val in enumerate(data.getTime()[:]):
        cmor.write(varid, data[index, :], time_vals=val, time_bnds=[
                climatology_bnds[index, :]])

    cmor.close(varid)