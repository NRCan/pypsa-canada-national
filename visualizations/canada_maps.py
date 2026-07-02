import geopandas as gpd
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.colors import ListedColormap

class canada_visualizations():
    def __init__(self):
        self.path = os.getcwd()
        self.vis_results = os.path.join(self.path, 'results', 'visualizations')

        # Read data
        zones = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'clustered_zone_data.feather')).reset_index()
        self.zones = gpd.GeoDataFrame(zones, geometry=zones.geometry, crs='EPSG: 4326')
        lines = gpd.read_feather(os.path.join(self.path, 'results', 'cluster_interfaces.feather'))
        self.lines = gpd.GeoDataFrame(lines, geometry=lines.geometry, crs='EPSG: 4326')
        nodes = gpd.read_feather(os.path.join(self.path, 'results', 'node_data.feather'))
        self.nodes = gpd.GeoDataFrame(nodes, geometry=nodes.geometry, crs='EPSG: 4326')
        generators = gpd.read_feather(os.path.join(self.vis_results, 'generator_data.feather'))
        self.generators = gpd.GeoDataFrame(generators, geometry=generators.geometry, crs='EPSG: 4326')

    def create_base_map(self, USA=False, annotated=False):
        territories = ['YT', 'NT', 'NU']
        zones = self.zones.copy().to_crs('EPSG: 3347')
        zones['colour'] = 'whitesmoke'
        zones.loc[zones.cluster.isin(territories), 'colour'] = 'gainsboro'

        fig, ax = plt.subplots(figsize = (100,100))
        ax.set_facecolor('skyblue')
        zones.plot(ax=ax, color=zones.colour, edgecolor='black', linewidth=0.5)
        if annotated:
            zones.apply(lambda x: ax.annotate(text=x['cluster'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)
        if USA:
            usa_map = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'usa_map.feather')).to_crs('EPSG: 3347')
            usa_map.plot(ax=ax, color='gainsboro', edgecolor='black', linewidth=0.5)
        return fig, ax

    def scaling(self, values, min_width, max_width):
        return (min_width + (values - values.min()) * (max_width - min_width) / (values.max() - values.min()))

    # PLOTS
    def plot_gridcells(self):
        # Colours for the gridcells
        fixed_colors = {
            'Both': 'purple',
            'Wind only': 'blue',
            'Solar only': 'orange'
        }
        colour_map = ListedColormap(plt.get_cmap('tab20').colors + plt.get_cmap('tab20b').colors)
        
        gridcells = gpd.read_feather(os.path.join(self.vis_results, 'filtered_gridcells.feather')).to_crs('EPSG: 3347')
        unused_cells = gridcells[gridcells.category == 'None']

        # wind/solar generators
        generators = self.generators.copy().to_crs('EPSG: 3347')
        generators = generators[(generators.gen_type == 'Solar PV') | (generators.gen_type == 'Onshore Wind')]
        generators['node_size'] = self.scaling(generators['p_nom'], 100, 1000)

        fig, ax = self.create_base_map(USA=False, annotated=False)
        # plot the max cells
        for category, colour in fixed_colors.items():
            subset = gridcells[gridcells.category == category]
            if not subset.empty:
                subset.plot(ax=ax, color=colour)
        # plot the other cells
        unused_cells.plot(ax=ax, column='cluster', cmap=colour_map, alpha=0.5, edgecolor='black')

        # Plot generator points
        generators.plot(ax=ax, 
                        color=generators['colour'], 
                        alpha=0.75,
                        markersize=generators['node_size'], 
                        edgecolor='black',
                        linewidth=1)

        plt.savefig(os.path.join(self.vis_results, 'gridcell_mapping.png'))

    def plot_potentials(self, type='PV'):
        gridcells = gpd.read_feather(os.path.join(self.vis_results, 'gridcells.feather')).to_crs('EPSG: 3347')
        lines = gpd.read_feather(os.path.join(self.path, 'results', 'testing', 'power_lines.feather')).to_crs('EPSG: 3347')

        # Filter cells with less than 10% onshore
        gridcells = gridcells[gridcells.percent_in_canada >= 0.5]
        # Filter cells close to transmission lines
        gridcells = gridcells[gridcells.close_to_grid]

        # wind/solar generators
        generators = self.generators.copy().to_crs('EPSG: 3347')
        if type == 'PV':
            generators = generators[(generators.gen_type.str.contains(type))]
        else:
            generators = generators[(generators.gen_type.str.contains(type.capitalize()))]
        generators['node_size'] = self.scaling(generators['p_nom'], 100, 1000)

        fig, ax = self.create_base_map(USA=False, annotated=False)
        
        gridcells.plot(ax=ax,
                    column=f'OPT_{type}',
                    cmap='plasma',
                    edgecolor='black',
                    alpha=0.75)

        # Plot generator points
        generators.plot(ax=ax, 
                        color=generators['colour'], 
                        alpha=0.75,
                        markersize=generators['node_size'], 
                        edgecolor='black',
                        linewidth=1)
        
        lines.plot(ax=ax,
                   color='black')

        plt.savefig(os.path.join(self.vis_results, f'potential_mapping_{type}.png'))

    def plot_generators(self):
        generators = gpd.read_feather(os.path.join(self.vis_results, 'generator_data.feather'))
        generators = gpd.GeoDataFrame(generators, geometry=generators.geometry, crs='EPSG: 4326').to_crs('EPSG: 3347')
        lines = self.lines.copy().to_crs('EPSG: 3347')

        ### PLOTTING with census regions
        fig, ax = self.create_base_map(USA=True, annotated=False)

        # Scale from 0 to 1
        lines['capacity'] = lines[['capacity_fwd', 'capacity_bck']].max(axis=1)
        lines['line_width'] = self.scaling(lines['capacity'], 3, 15)

        generators['node_size'] = self.scaling(generators['p_nom'], 100, 10000)

        # Plot transmission lines
        lines.plot(ax=ax, 
                   color='dimgray', 
                   linewidth=lines.line_width)
        
        # Plot generator points
        generators.plot(ax=ax, 
                        color=generators['colour'], 
                        alpha=0.75,
                        markersize=generators['node_size'], 
                        edgecolor='black',
                        linewidth=1)
        # Legend
        generator_legend_elements = [
                            mlines.Line2D(
                            [], [], 
                            color='black',             # edge color
                            marker='o',                # circle marker
                            markerfacecolor=color,     # fill color
                            markersize=60,             # size in legend
                            label=gen_type,
                            linewidth=0,
                            alpha=0.75                # no line, just marker
                        )
                        for gen_type, color in generators.groupby('gen_type')['colour'].first().items()
                        ]
        line_legend_elements = mlines.Line2D([], [], color='dimgray', linewidth=10, linestyle='-', label='Transmission')
        legend_elements = generator_legend_elements + [line_legend_elements]
        ax.legend(handles=legend_elements, fontsize=50, markerscale=1)
        
        # Saving plot
        plt.savefig(os.path.join(self.vis_results, 'generator_capacity_Canada.png'))

    def plot_industrial_loads(self):
        loads = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'industrial_loads.feather'))
        zones = self.zones.copy()
        lines = self.lines.copy()

        ### PLOTTING with census regions
        fig, ax = plt.subplots(figsize = (150,150))
        zones.plot(ax=ax, color=zones['colour'], edgecolor='black')
        zones.apply(lambda x: ax.annotate(text=x['cluster'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)

        # Scale from 0 to 1
        lines['capacity'] = lines[['capacity_fwd', 'capacity_bck']].max(axis=1)
        lines['line_width'] = self.scaling(lines['capacity'], 1, 25)

        loads['node_size'] = self.scaling(loads['load'], 100, 10000)

        lines.plot(ax=ax, color='black', linewidth=lines.line_width)
        loads.plot(ax=ax, column='NAICS Code Description', cmap='tab20', markersize=loads['node_size'], legend=True, legend_kwds={'fontsize': 50, 'markerscale':10})

        plt.savefig(os.path.join(self.path, 'results', 'visualizations', 'industrial_loads_Canada.png'))

    def plot_hydro_basins(self):
        hydro_basins = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'river_basins.feather')).to_crs('EPSG: 3347')
        hydro_generators = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'hydro_generators.feather')).to_crs('EPSG: 3347')
        used_basins = pd.read_csv(os.path.join(self.path, 'results', 'testing', 'ror_energy_check.csv'), index_col=0)

        fig, ax = self.create_base_map(USA=False, annotated=False)
        hydro_basins.plot(ax=ax)
        hydro_basins[hydro_basins.COMID.isin(used_basins.COMID)].plot(ax=ax, color='red')
        hydro_generators.plot(ax=ax, color='black', markersize=50)
        #hydro_generators.apply(lambda x: ax.annotate(text=x['cluster'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)
        plt.savefig(os.path.join(self.path, 'results', 'visualizations', 'hydro_basins_Canada.png'))
    
    def plot_hydro_reservoirs(self):
        hydro_basins = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'river_basins.feather'))
        hydro_generators = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'hydro_storage.feather'))
        hydro_reservoirs = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'hydro_reservoirs.feather'))
        zones = self.zones.copy()

        fig, ax = plt.subplots(figsize = (200,200))
        zones.plot(ax=ax, color='whitesmoke', edgecolor='black')
        zones.apply(lambda x: ax.annotate(text=x['cluster'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)
        hydro_generators.plot(ax=ax, color='red', markersize=100)
        hydro_reservoirs.plot(ax=ax, color='blue')
        hydro_basins.plot(ax=ax, color='lightblue', alpha=0.6)
        plt.savefig(os.path.join(self.path, 'results', 'visualizations', 'hydro_reservoirs_Canada.png'))

    def plot_dams(self):
        generators = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'generator_data.feather'))
        generators = gpd.GeoDataFrame(generators, geometry=generators.geometry, crs='EPSG: 4326').to_crs('EPSG: 3347')
        generators = generators[generators.gen_type.str.contains('Hydro')]

        dams = gpd.read_feather(os.path.join(self.path, 'results', 'visualizations', 'dam_map.feather')).to_crs('EPSG: 3347')

        ### PLOTTING with census regions
        fig, ax = self.create_base_map(USA=True, annotated=False)

        generators['node_size'] = self.scaling(generators['p_nom'], 10, 100)
        # Plot generator points
        generators.plot(ax=ax, 
                        color='blue',
                        alpha=0.75,
                        markersize=generators['node_size'], 
                        edgecolor='black',
                        linewidth=1)
        
        dams['node_size'] = self.scaling(dams['CAP_MCM'], 10, 100)
        dams.plot(ax=ax, 
                        color='red', 
                        alpha=0.75,
                        markersize=dams['node_size'], 
                        edgecolor='black',
                        linewidth=1)
        
        # Saving plot
        plt.savefig(os.path.join(self.path, 'results', 'visualizations', 'hydro_gens_dams.png'))

    def plot_canvec_data(self):
        lines = gpd.read_feather(os.path.join(self.path, 'results', 'testing', 'power_lines.feather')).to_crs('EPSG: 3347')
        transformers = gpd.read_feather(os.path.join(self.path, 'results', 'testing', 'transformer_data_0.feather')).to_crs('EPSG: 3347')

        # Draw buffer zone around lines and transformers
        buffered_lines = gpd.GeoDataFrame(geometry=[lines.geometry.buffer(20000).union_all()], crs=lines.crs)
        buffered_transformers = gpd.GeoDataFrame(geometry=[transformers.buffer(20000).union_all()], crs=transformers.crs)

        print('Plotting')
        fig, ax = self.create_base_map(USA=False, annotated=False)
        lines.plot(ax=ax, color='blue')
        transformers.plot(ax=ax, color='red')

        buffered_lines.plot(ax=ax, color='blue', alpha=0.5)
        buffered_transformers.plot(ax=ax, color='red', alpha=0.5)

        plt.savefig(os.path.join(self.vis_results, 'canvec_data.png'))

if __name__ == '__main__':
    vis = canada_visualizations()
    #vis.plot_industrial_loads()
    #vis.plot_generators()
    #vis.plot_hydro_basins()
    #vis.plot_hydro_reservoirs()
    #vis.plot_dams()
    vis.plot_gridcells()
    #vis.plot_potentials(type='PV')
    #vis.plot_potentials(type='wind')
    #vis.plot_canvec_data()