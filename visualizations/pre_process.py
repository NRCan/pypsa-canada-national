import geopandas as gpd
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from shapely import LineString, Point, Polygon
from shapely.geometry import box

def clip_by_lat(geom, min_lon, max_lon, min_lat, max_lat):
    # Create a horizontal "cut" line at cutoff latitude
    # bounding box for everything south of cutoff latitude (latitude < cutoff)
    bbox = box(min_lon, min_lat, max_lon, max_lat)
    # intersect the geometry with bbox to clip off northern part
    return geom.intersection(bbox)

def add_territories():
    path = os.getcwd()
    zones = gpd.read_feather(os.path.join(path, 'results', 'clustered_zone_data.feather'))
    census_areas = gpd.read_file(os.path.join(path, 'data', 'map_files', 'census_map', 'lcd_000b21a_e.shp')).to_crs('EPSG: 4326')
    territories = census_areas[census_areas.PRUID.astype(int) >= 60]
    territories = territories.dissolve(by='PRUID', aggfunc='first')
    # Apply clipping to your geometries
    #territories['geometry'] = territories['geometry'].apply(lambda geom: clip_by_lat(geom, -142, -53, 38, 61))
    zones = pd.concat([zones, territories])
    zones.to_feather(os.path.join(path, 'results', 'visualization_data', 'clustered_zone_data.feather'))

def add_usa():
    path = os.getcwd()
    usa_map = gpd.read_file(os.path.join(path, 'data', 'map_files', 'USA_map', 'cb_2018_us_state_5m.shp')).to_crs('EPSG: 4326')
    #usa_map = gpd.GeoDataFrame(usa_map, geometry=usa_map.geometry, crs='EPSG: 4326')
    usa_map['geometry'] = usa_map['geometry'].apply(lambda geom: clip_by_lat(geom, -142, -53, 35, 90)) 
    #usa_map['geometry'] = usa_map['geometry'].apply(lambda geom: clip_by_lat(geom, -170, -65, 0, 90)) # Alaska
    usa_map.to_feather(os.path.join(path, 'results', 'visualization_data', 'usa_map.feather'))

def set_zone_colours():
    province_colours = {
    'YT': mcolors.CSS4_COLORS['grey'],
    'NT': mcolors.CSS4_COLORS['grey'],
    'NU': mcolors.CSS4_COLORS['grey'],
    'BC': mcolors.TABLEAU_COLORS['tab:blue'],
    'AB': mcolors.TABLEAU_COLORS['tab:brown'],
    'SK': mcolors.TABLEAU_COLORS['tab:green'],
    'MB': mcolors.TABLEAU_COLORS['tab:purple'],
    'ON': mcolors.TABLEAU_COLORS['tab:red'],
    'QC': '#003399',
    'NB': mcolors.TABLEAU_COLORS['tab:orange'],
    'NS': mcolors.TABLEAU_COLORS['tab:pink'],
    'PE': mcolors.TABLEAU_COLORS['tab:cyan'],
    'NL': mcolors.TABLEAU_COLORS['tab:gray'],
    }

    path = os.getcwd()
    # Read data
    zones = gpd.read_feather(os.path.join(path, 'results', 'visualizations', 'clustered_zone_data.feather')).rename(index={'60': 'YT', '61': 'NT', '62':'NU'}).reset_index()
    zones = zones.rename(columns={'index':'cluster'})
    zones['province'] = zones.cluster.str[:2]
    regions = zones['province'].unique()
    base_cmap = plt.get_cmap('tab10')
    region_to_base_colour = {region: province_colours.get(region, base_cmap(i % base_cmap.N)) for i, region in enumerate(regions)}
    
    def generate_shades(base_colour, n_shades):
        base_hsv = mcolors.rgb_to_hsv(mcolors.to_rgb(base_colour))
        saturations = np.linspace(0.5, 1.0, n_shades)
        shades = [mcolors.hsv_to_rgb((base_hsv[0], s, base_hsv[2])) for s in saturations]
        return [mcolors.to_hex(shade) for shade in shades]

    custom_colour_map = {}
    for region in regions:
        base_colour = region_to_base_colour[region]
        region_clusters = zones[zones.province == region]['cluster']
        shades = generate_shades(base_colour, len(region_clusters))
        for name, shade in zip(region_clusters, shades):
            custom_colour_map[name] = shade
    zones['colour'] = zones['cluster'].map(custom_colour_map)
    zones = zones.set_index('cluster', drop=True)
    zones.to_feather(os.path.join(path, 'results', 'visualizations', 'clustered_zone_data.feather'))

def create_interface_lines():
    path = os.getcwd()
    ### Creating interface lines
    interfaces = pd.read_csv(os.path.join(path, 'results', 'cluster_interfaces.csv'))
    nodes = gpd.read_feather(os.path.join(path, 'results', 'visualization_data', 'nearest_nodes.feather'))
    interfaces = interfaces.merge(nodes['geometry'], how='left', left_on='start', right_index=True)
    interfaces = interfaces.merge(nodes['geometry'], how='left', left_on='end', right_index=True, suffixes=['_1', '_2'])
    interfaces['geometry'] = interfaces.apply(lambda row: LineString([row['geometry_1'], row['geometry_2']]), axis=1)
    gpd.GeoDataFrame(interfaces).drop(['geometry_1', 'geometry_2'], axis=1).to_feather(os.path.join(path, 'results', 'visualization_data', 'cluster_interfaces.feather'))

def generators():
    gen_type_map = {
        'biomass': 'Biomass',
        'Biomass': 'Biomass',
        'MSW': 'Biomass',
        'NG_CC': 'Gas',
        'NG_CG': 'Gas', # Need to change
        'NG_SC': 'Gas', # Need to confirm
        'biogas': 'Biomass',
        'coal': 'Coal', # Need to confirm/change
        'coal_CCS': 'Coal', # Need to add new type
        'diesel_CT': 'Diesel',
        'gasoline_CT': 'Diesel', # Need to add new type?
        'hydro_daily': 'Reservoir Hydro',
        'hydro_monthly': 'Reservoir Hydro',
        'hydro_run': 'River Hydro',
        'nuclear': 'Nuclear',
        'oil_CT': 'Oil', # Need to add new type?
        'oil_ST': 'Oil',
        'solar_PV': 'Solar PV',
        'wind_ons': 'Onshore Wind'
        }
    
    gen_type_color = {
        'Biomass': mcolors.CSS4_COLORS['hotpink'],
        'Gas': mcolors.CSS4_COLORS['salmon'],
        'Coal': mcolors.CSS4_COLORS['saddlebrown'],
        'Diesel': mcolors.CSS4_COLORS['sandybrown'],
        'Oil': mcolors.CSS4_COLORS['black'],
        'Nuclear': mcolors.CSS4_COLORS['springgreen'],
        'Reservoir Hydro': mcolors.CSS4_COLORS['royalblue'],
        'River Hydro': mcolors.CSS4_COLORS['dodgerblue'],
        'Solar PV': mcolors.CSS4_COLORS['yellow'],
        'Onshore Wind': mcolors.CSS4_COLORS['beige']
    }

    path = os.getcwd()
    nodes = gpd.read_feather(os.path.join(path, 'results', 'node_data.feather'))
    
    # Both storage units and generators included
    generator_data = pd.read_csv(os.path.join(path, 'data', 'CODERS', 'generators.csv'), index_col=0)
    # Find cluster
    generator_data = pd.merge(generator_data, nodes[['cluster', 'geometry']], how='left', left_on='network_node_code', right_index=True)
    # Check if entries are unique, some aren't due to co-location, bad naming and different start/close years
    generators = generator_data.groupby(['generation_facility_name', 'gen_type', 'facility_installed_capacity']).first()
    generators['p_nom'] = generator_data.groupby(['generation_facility_name', 'gen_type', 'facility_installed_capacity'])['unit_installed_capacity'].sum()
    generators = generators.reset_index()
    # Map generation types
    generators.loc[:, 'gen_type'] = generators.loc[:, 'gen_type'].map(gen_type_map)
    generators['colour'] = generators['gen_type'].map(gen_type_color)
    generators = gpd.GeoDataFrame(generators).to_feather(os.path.join(path, 'results', 'visualization_data', 'generator_data.feather'))

def industrial_loads():
    load_type_map = {
        'In-situ oil sands extraction': 'Oil Sands',
        'Iron and Steel Mills and Ferro-Alloy Manufacturing': 'Steelmaking',
        'Primary Production of Alumina and Aluminum': 'Aluminum',
        'Cement Manufacturing': 'Cement Manufacturing',
        'Lime Manufacturing': 'Lime Manufacturing',
        'Gold and Silver Ore Mining': 'Gold and Silver Mining',
        'Potash Mining': 'Potash Mining',
        'Petroleum Refineries': 'Refinery',
        'Mined oil sands extraction': 'Oil Sands',
        'Iron Ore Mining': 'Iron Ore Mining',
        'Non-Ferrous Metal (except Aluminum) Smelting and Refining': 'Non-Ferrous Smelting',
        'Other Basic Organic Chemical Manufacturing': 'Chemicals',
        'Paperboard Mills': 'Pulp & Paper',
        'Paper Bag and Coated and Treated Paper Manufacturing': 'Pulp & Paper',
        'Newsprint Mills': 'Pulp & Paper',
        'Resin and Synthetic Rubber Manufacturing': 'Chemicals',
        'Chemical Pulp Mills': 'Pulp & Paper',
        'Industrial Gas Manufacturing': 'Chemicals',
        'Petrochemical Manufacturing': 'Chemicals',
        'Pharmaceutical and Medicine Manufacturing': 'Chemicals',
        'All Other Basic Inorganic Chemical Manufacturing': 'Chemicals',
        'Sanitary Paper Product Manufacturing': 'Pulp & Paper',
        'Paper (except Newsprint) Mills': 'Pulp & Paper',
        'All Other Miscellaneous Chemical Product Manufacturing': 'Chemicals',
        'Chemical Fertilizer (except Potash) Manufacturing': 'Chemicals',
        'All Other Converted Paper Product Manufacturing': 'Pulp & Paper',
        'Mechanical Pulp Mills': 'Pulp & Paper',
        'Artificial and Synthetic Fibres and Filaments Manufacturing': 'Chemicals',
        'Alkali and Chlorine Manufacturing': 'Chemicals',
        'Paint and Coating Manufacturing': 'Chemicals'
    }
    path = os.getcwd()
    load = gpd.read_feather(os.path.join(path, 'results', 'visualization_data', 'all_industries_loads.feather'))
    load['NAICS Code Description'] = load['NAICS Code Description'].map(load_type_map)
    load.to_feather(os.path.join(path, 'results', 'visualization_data', 'industrial_loads.feather'))    

def hydro_basins():
    path = os.getcwd()
    basins = gpd.read_file(os.path.join(path, 'data', 'map_files', 'MERIT_basins', 'riv_pfaf_7_MERIT_Hydro_v07_Basins_v01.shp'))
    zones = gpd.read_feather(os.path.join(path, 'results', 'clustered_zone_data.feather')).reset_index()
    basins = gpd.sjoin(basins, zones, how="inner", predicate="within")
    basins.to_feather(os.path.join(path, 'results', 'visualization_data', 'river_basins.feather'))

def classify_max_wind_solar():
    path = os.getcwd()
    # Max gridcells
    gridcells = gpd.read_feather(os.path.join(path, 'results', 'visualization_data', 'filtered_gridcells.feather'))
    df = pd.DataFrame()
    wind_cfs = pd.read_csv(os.path.join(path, 'results', 'max_cfs_wind.csv'))
    solar_cfs = pd.read_csv(os.path.join(path, 'results', 'max_cfs_solar.csv'))
    df['wind'] = wind_cfs.columns.str.split('-').str[-1].astype(int)
    df['solar'] = solar_cfs.columns.str.split('-').str[-1].astype(int)

    # Extract sets of gridcell numbers for wind and solar
    wind_cells = set(df['wind'].dropna().unique())
    solar_cells = set(df['solar'].dropna().unique())

    # Define function to classify each gridcell number
    def classify_cell(cell_num):
        in_wind = cell_num in wind_cells
        in_solar = cell_num in solar_cells
        if in_wind and in_solar:
            return 'Both'
        elif in_wind:
            return 'Wind only'
        elif in_solar:
            return 'Solar only'
        else:
            return 'None'
    gridcells['category'] = gridcells.index.to_series().apply(classify_cell)
    gridcells.to_feather(os.path.join(path, 'results', 'visualizations', 'filtered_gridcells.feather'))

def average_wind_solar():
    path = os.getcwd()
    gridcells = gpd.read_feather(os.path.join(path, 'results', 'visualizations', 'gridcells.feather'))

    for col in ['OPT_wind', 'OPT_PV']:
        if col in gridcells.columns:
            gridcells = gridcells.drop(columns=[col])

    solar_cf = pd.read_csv(os.path.join(path, 'results', 'testing', 'OPT_PV_average_cf.csv'), index_col=0)
    solar_cf['OPT_PV'] = solar_cf['OPT_PV'].divide(solar_cf.OPT_PV.max())
                                                   
    wind_cf = pd.read_csv(os.path.join(path, 'results', 'testing', 'OPT_wind_average_cf.csv'), index_col=0)
    wind_cf['OPT_wind'] = wind_cf['OPT_wind'].divide(wind_cf.OPT_wind.max())

    gridcells = gridcells.merge(solar_cf, how='left', left_index=True, right_index=True)
    gridcells = gridcells.merge(wind_cf, how='left', left_index=True, right_index=True)

    gridcells.to_feather(os.path.join(path, 'results', 'visualizations', 'gridcells.feather'))

def simple_canada_map():
    path = os.getcwd()
    simple_canada_map = gpd.read_file(os.path.join(path, 'data', 'map_files', 'simple_canada_map', 'ca.shp'))
    simple_canada_map = gpd.GeoDataFrame(simple_canada_map, geometry=simple_canada_map.geometry, crs='EPSG:4326')
    simple_canada_map.to_feather(os.path.join(path, 'results', 'visualizations', 'simple_canada_map.feather'))

def canvec_data():
    path = os.getcwd()
    transmission_data = gpd.read_file(os.path.join(path, 'data', 'map_files', 'Canvec', 'power_line_1.shp'))
    transmission_data = gpd.GeoDataFrame(transmission_data, geometry=transmission_data.geometry).to_crs('EPSG:4326')
    transmission_data.to_feather(os.path.join(path, 'results', 'visualization_data', 'power_lines.feather'))

    # transformer_data = gpd.read_file(os.path.join(path, 'data', 'map_files', 'Canvec', 'transformer_station_0.shp'))
    # transformer_data = gpd.GeoDataFrame(transformer_data, geometry=transformer_data.geometry).to_crs('EPSG:4326')
    # transformer_data.to_feather(os.path.join(path, 'results', 'testing', 'transformer_data_0.feather'))

if __name__ == '__main__':
    #add_territories()
    #add_usa()
    #set_zone_colours()
    #create_interface_lines()
    #generators()
    #industrial_loads()
    hydro_basins()
    #classify_max_wind_solar()
    #average_wind_solar()
    #simple_canada_map()
    #canvec_data()