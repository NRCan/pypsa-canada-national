import geopandas as gpd
import os
import matplotlib.pyplot as plt

def plot_clusters(zones, lines, nodes, name):
    ### PLOTTING with census regions
    fig, ax = plt.subplots(figsize = (100,100))
    zones.plot(ax=ax, column='leiden_cluster', cmap='tab20')
    zones.apply(lambda x: ax.annotate(text=x['CSDNAME'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)
    lines.plot(ax=ax, color='blue', markersize=50)
    HV_lines = lines[(lines.voltage >= 200)]
    if not HV_lines.empty:
        gpd.GeoDataFrame(HV_lines).set_geometry('geometry').plot(ax=ax, color='black', markersize=50)
    nodes.plot(ax=ax, color='black', markersize=50) #Nodes
    
    plt.savefig(os.path.join(path, 'results', 'provincial', f'{name}_leiden_cluster_voltage_w_HV.png'))



def plot_clusters(zones, lines, nodes, name):
        ### PLOTTING with census regions
        fig, ax = plt.subplots(figsize = (100,100))
        zones.plot(ax=ax, column='leiden_cluster', cmap='tab20')
        zones.apply(lambda x: ax.annotate(text=x['CSDNAME'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)
        lines.plot(ax=ax, color='blue', markersize=50)
        HV_lines = lines[(lines.voltage >= 200)]
        if not HV_lines.empty:
            gpd.GeoDataFrame(HV_lines).set_geometry('geometry').plot(ax=ax, color='black', markersize=50)
        nodes.plot(ax=ax, color='black', markersize=50) #Nodes
        
        plt.savefig(os.path.join(path, 'results', 'provincial', f'{name}_leiden_cluster_voltage_w_HV.png'))



def plot_clusters(zones, lines, nodes, name):
        ### PLOTTING with census regions
        fig, ax = plt.subplots(figsize = (150,150))
        zones.plot(ax=ax, column='cluster', cmap='viridis')
        zones.apply(lambda x: ax.annotate(text=x['cluster'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)
        lines.plot(ax=ax, color='blue', markersize=50)
        HV_lines = lines[(lines.voltage >= 200)]
        if not HV_lines.empty:
            gpd.GeoDataFrame(HV_lines).set_geometry('geometry').plot(ax=ax, color='black', markersize=50)
        nodes.plot(ax=ax, color='black', markersize=50) #Nodes
        
        plt.savefig(os.path.join(path, 'results', 'visualizations', f'{name}_leiden_cluster_w_HV.png'))



def plot_transfer_capacities(zones, lines, nodes, name):
        ### PLOTTING with census regions
        fig, ax = plt.subplots(figsize = (150,150))
        zones.plot(ax=ax, column='cluster', cmap='tab20')
        zones.apply(lambda x: ax.annotate(text=x['cluster'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)
        # Scale from 0 to 1
        min_width = 15
        max_width = 50
        lines['line_width'] = (lines.capacity - lines.capacity.min()) * (max_width - min_width) / (lines.capacity.max() - lines.capacity.min())

        lines.plot(ax=ax, color='blue', linewidth=lines.line_width)
        nodes.plot(ax=ax, color='black', markersize=50) #Nodes
        
        plt.savefig(os.path.join(path, 'results', 'visualizations', f'transfer_capacity_{name}.png'))




def plot(zones, lines, nodes, name):
        ### PLOTTING with census regions
        fig, ax = plt.subplots(figsize = (150,150))
        zones.plot(ax=ax, column='cluster', cmap='tab20')
        zones.apply(lambda x: ax.annotate(text=x['cluster'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)
        # Scale from 0 to 1
        min_width = 50
        max_width = 75
        min_cap = lines.capacity.min() - 1
        lines['line_width'] = (lines.capacity - min_cap) * (max_width - min_width) / (lines.capacity.max() - min_cap)

        lines.plot(ax=ax, color='blue', linewidth=lines.line_width)
        nodes.plot(ax=ax, color='black', markersize=50) #Nodes
        
        plt.savefig(os.path.join(path, 'results', 'visualizations', f'transfer_capacity_{name}.png'))

def mapLines(data):  #given a dataframe with 2 sets of lon/lat co-ords
    geometry = [LineString(xy) for xy in zip(data.geometry_1, data.geometry_2)]
    geo_df = gpd.GeoDataFrame(data, crs = {'init':'EPSG:4326'}, geometry = geometry)
    geo_df = geo_df.drop(['geometry_1', 'geometry_2'], axis=1)
    return geo_df #returns a geopandas dataframe with the line geometries assigned

### LOAD FILES
path = os.getcwd()
cluster_data = gpd.read_feather(os.path.join(path, 'results', 'clustered_zone_data.feather')).to_crs('EPSG: 4326')
nearest_nodes = gpd.read_feather(os.path.join(path, 'results', 'nearest_nodes.feather')).to_crs('EPSG: 4326')
transfer_capacities = pd.read_csv(os.path.join(path, 'results', 'transfer capacities.csv'))

transfer_capacities = transfer_capacities.merge(nearest_nodes['geometry'], how='left', left_on='cluster_1', right_on='cluster')
transfer_capacities = transfer_capacities.merge(nearest_nodes['geometry'], how='left', left_on='cluster_2', right_on='cluster', suffixes=['_1', '_2'])
transfer_capacities = mapLines(transfer_capacities)

plot(cluster_data.reset_index(), transfer_capacities, nearest_nodes, 'Canada')


# Reading census area shapefile
path = os.getcwd()
all_lines = gpd.read_feather(os.path.join(path, 'results', 'line_data.feather')).to_crs('EPSG: 4326')
zone_data = gpd.read_feather(os.path.join(path, 'results', 'clustered_zone_data.feather')).to_crs('EPSG: 4326').reset_index()
node_data = gpd.read_feather(os.path.join(path, 'results', 'node_data.feather')).to_crs('EPSG: 4326').reset_index()
cluster_data = pd.read_csv(os.path.join(path, 'results', 'manual_cluster_data.csv'), index_col=0)
generators = pd.read_csv(os.path.join(path, 'data', 'CODERS', 'generators.csv'))

province = 'QC'
zone_data = zone_data[zone_data.province.str.contains(province)]

all_lines = all_lines[(all_lines.province_1 == province) | (all_lines.province_2 == province)]
all_lines = all_lines.merge(cluster_data['manual_cluster'], how='left', left_on='CDUID_1', right_index=True)
all_lines = all_lines.merge(cluster_data['manual_cluster'], how='left', left_on='CDUID_2', right_index=True, suffixes=['_1', '_2'])
HV_lines = all_lines[(all_lines.manual_cluster_1 != all_lines.manual_cluster_2)]
HV_lines = HV_lines[(HV_lines.voltage >= 100)]

node_data = node_data[(node_data.node_code.isin(HV_lines.node_1)) | (node_data.node_code.isin(HV_lines.node_2))]
generators = generators[(generators.network_node_code.isin(node_data.node_code))]
generators['geometry'] = [Point(xy) for xy in zip(generators['longitude'], generators['latitude'])]
generators = gpd.GeoDataFrame(generators, crs = {'init':'EPSG:4326'}, geometry = generators.geometry)

### PLOTTING with census regions
fig, ax = plt.subplots(figsize = (150,150))
## Normalize category
zone_data.plot(ax=ax, column='cluster', cmap='tab20')
zone_data.apply(lambda x: ax.annotate(text=x['cluster'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=15), axis=1)
all_lines.plot(ax=ax, color='red', markersize=10)
if not HV_lines.empty:
    gpd.GeoDataFrame(HV_lines).set_geometry('geometry').plot(ax=ax, color='black', markersize=25)

node_data.plot(ax=ax, color='black', markersize=25) #Nodes
node_data.apply(lambda x: ax.annotate(text=x['node_code'], xy=x.geometry.centroid.coords[0], fontsize=10), axis=1)

generators.plot(ax=ax, color='yellow')

plt.savefig(os.path.join(path, 'results', 'provincial', f'{province}_MAP.png'))



def plot_clusters(zones, lines, nodes, name, category, colourmap):
        ### PLOTTING with census regions
        fig, ax = plt.subplots(figsize = (50,50))
        ## Normalize category
        zones.plot(ax=ax, column=category, cmap=colourmap)
        #zones.apply(lambda x: ax.annotate(text=x['CDUID'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=10), axis=1)
        lines.plot(ax=ax, color='blue', markersize=25)
        HV_lines = lines[(lines.voltage >= 200)]
        if not HV_lines.empty:
            gpd.GeoDataFrame(HV_lines).set_geometry('geometry').plot(ax=ax, color='black', markersize=25)
        nodes.plot(ax=ax, color='black', markersize=25) #Nodes
        
        plt.savefig(os.path.join(path, 'results', 'provincial', f'{name}_{category}.png'))

# Reading census area shapefile
path = os.getcwd()
all_lines = gpd.read_feather(os.path.join(path, 'results', 'line_data.feather')).to_crs('EPSG: 4326')
zone_data = gpd.read_feather(os.path.join(path, 'results', 'zone_data.feather')).to_crs('EPSG: 4326')
node_data = gpd.read_feather(os.path.join(path, 'results', 'node_data.feather')).to_crs('EPSG: 4326')

province = 'AB'
categories = {'population':'Reds', 'hydro_generation':'Blues', 'nuclear_generation':'Greens', 'solar_generation':'YlOrBr', 'thermal_generation':'Greys', 'wind_generation':'Purples'}

zone_data = zone_data[zone_data.province == province]
all_lines = all_lines[(all_lines.province_1 == province) & (all_lines.province_2 == province)]
node_data = node_data[node_data.province == province]

for category, colourmap in categories.items():
    if zone_data[category].sum() == 0:
         continue
    else:
        plot_clusters(zone_data.reset_index(), all_lines, node_data, province, category, colourmap)




#Degree spacing between grid cells
latDeg = 0.5
lonDeg = 0.625
gridcells = gridcells.to_crs('EPSG: 4326')
polys = []
#convert grid cell points to grid cell polygons
for index, row in gridcells.iterrows():
    lat = row.geometry.y
    lon = row.geometry.x
    #for each grid cell point, create a rectangular polygon using point as lower left
    lats = [lat - latDeg/2, lat + latDeg/2, lat + latDeg/2, lat - latDeg/2] 
    lons = [lon - lonDeg/2, lon-lonDeg/2, lon + lonDeg/2, lon + lonDeg/2]
    poly_geom = Polygon(zip(lons, lats))
    polys.append(poly_geom)

gridcells['geometry'] = pd.Series(polys)
gridcells = gridcells.reset_index()
gridcells = gpd.GeoDataFrame(gridcells[['grid cell', 'cluster']], geometry=gridcells['geometry'])
### PLOTTING with census regions
fig, ax = plt.subplots(figsize = (50,50))
gridcells.plot(ax=ax, column='cluster', cmap='tab20')
gridcells.apply(lambda x: ax.annotate(text=x['grid cell'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=15), axis=1)

plt.savefig(os.path.join(path, 'results', 'visualizations', 'grid_cell_testing.png'))