import geopandas as gpd
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.cm as cm
import matplotlib.colors as colors

class canada_visualizations():
    def __init__(self):
        self.path = os.getcwd()
        #self.results_path = Path(r"C:\Users\ndematos\Desktop\REED_scenarios\Reference\Output")
        #self.results = pd.read_csv(os.path.join(self.results_path, "post_process_planning", 'Nodal_summary_planning.csv'))
        self.results = pd.read_csv(r"C:\Users\ndematos\Desktop\REED_scenarios\no-CER-hydro_fix.csv")

        self.vis_results = os.path.join(self.path, 'results', 'visualizations')

        # Read data
        zones = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'clustered_zone_data.feather')).reset_index()
        self.zones = gpd.GeoDataFrame(zones, geometry=zones.geometry, crs='EPSG: 4326').rename(columns={'index':'cluster'})
        lines = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'cluster_interfaces.feather'))
        self.lines = gpd.GeoDataFrame(lines, geometry=lines.geometry, crs='EPSG: 4326')
        nodes = gpd.read_feather(os.path.join(self.path, 'results', 'node_data.feather'))
        self.nodes = gpd.GeoDataFrame(nodes, geometry=nodes.geometry, crs='EPSG: 4326')
        generators = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'generator_data.feather'))
        self.generators = gpd.GeoDataFrame(generators, geometry=generators.geometry, crs='EPSG: 4326')


        self.tech_colors = {
            'Natural Gas': '#ff6b6b',
            'Solar PV': '#ffff99',
            'Lithium-ion Battery': '#6a3d9a',
            'Onshore Wind': '#b2df8a',
            'Nuclear': '#ff7f00',
            'Oil': '#ffaa33',
            'Hydro': '#a6cee3',
            'Coal': '#b15928',
            'Biomass': '#33a02c',
            'Diesel': '#000000',
            'Other Combustion': '#b15928',
            'Load Shed': '#b15928'
        }

        self.tech_map = {
        'default_liion_battery':'Lithium-ion Battery',
        'default_solar_PV': 'Solar PV',
        'gas_CC': 'Natural Gas',
        'gas_CT': 'Natural Gas',
        'wind_new': 'Onshore Wind',
        'default_nuclear': 'Nuclear',
        'default_oil': 'Oil',
        'default_diesel': 'Diesel',
        'hydro_ror': 'Hydro',
        'hydro_storage': 'Hydro',
        'coal_IGCC': 'Coal',
        'default_biogas': 'Biomass',
        'default_biomass': 'Biomass',
        'wind_2021': 'Onshore Wind',
        'load_shedding': 'Natural Gas'
        }

    def create_base_map(self, USA=False, annotated=False):
        territories = ['60', '61', '62']
        zones = self.zones.copy().to_crs('EPSG: 3347')
        zones['colour'] = 'whitesmoke'
        zones.loc[zones.cluster.isin(territories), 'colour'] = 'white'

        fig, ax = plt.subplots(figsize = (100,100))
        ax.set_facecolor('white')
        zones.plot(ax=ax, color=zones.colour, edgecolor='black', linewidth=1)
        if annotated:
            zones.apply(lambda x: ax.annotate(text=x['cluster'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=30), axis=1)
        if USA:
            usa_map = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'usa_map.feather')).to_crs('EPSG: 3347')
            usa_map.plot(ax=ax, color='white', edgecolor='black', linewidth=1)
        return fig, ax

    def scaling(self, values, min_width, max_width):
        return (min_width + (values - values.min()) * (max_width - min_width) / (values.max() - values.min()))

    # PLOTS
    def plot_base(self):
        fig, ax = plt.subplots(figsize = (100,100))
        ax.set_facecolor('white')
        zones = gpd.read_file(os.path.join(self.path, 'data', 'map_files', 'census_map', 'lcd_000b21a_e.shp')).to_crs('EPSG: 3347')
        zones['colour'] = 'whitesmoke'
        zones.plot(ax=ax, color=zones.colour, edgecolor='black', linewidth=1) 
        plt.savefig(os.path.join(self.vis_results, f'base_map.png'))

    def plot_prices(self, year):
        prices = pd.read_csv(os.path.join(self.results_path, f'output_{year}', 'buses-marginal_price.csv'), index_col=0)
        prices = prices.replace({1000000: 0, 850000.0005029261: 0, 722500.0008549744: 0})
        mean_price = prices.mean()
        mean_price.name = 'zonal_prices'
        mean_price = pd.merge(self.zones.to_crs('EPSG: 3347'), mean_price, left_on='cluster', right_index=True)
        
        fig, ax = self.create_base_map(USA=False, annotated=False)
        mean_price.plot(ax=ax,
                        column='zonal_prices',
                        cmap='plasma',
                        edgecolor='black',
                        alpha=0.75,
                        legend=True)

        plt.savefig(os.path.join(self.vis_results, f'zonal_prices_{year}.png'))

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

    def plot_lines(self, year, new):
        lines = self.lines.copy().to_crs('EPSG: 3347')
        lines.index = lines.start + '->' + lines.end
        results = self.results.copy()
        results = results[results.Parameter.isin(['New_Transmission_Capacity', 'Transmission_Capacity'])]
        results.loc[:, 'Time'] = results.Time.astype(int)
        if new:
            print('Plotting New Capacity')
            capacity = results[results.Parameter == 'New_Transmission_Capacity']
            capacity = capacity[capacity.Time <= year]
            capacity = capacity.groupby(['Region', 'Parameter', 'Variable'])['Value'].sum()
            capacity = capacity.reset_index()
            name = 'new'
        else:
            capacity = results[results.Parameter == 'Transmission_Capacity']
            capacity = capacity[capacity.Time == year]
            name = 'total'
            
        capacity = capacity.set_index('Region')
        capacity = capacity['Value']

        line_colour = 'darkturquoise'

        fig, ax = self.create_base_map(USA=True, annotated=False)

        if year == '2021':
            # Scale from 0 to 1
            lines['capacity'] = lines[['capacity_fwd', 'capacity_bck']].max(axis=1)
        else:
            capacity.name = 'capacity'
            lines = pd.merge(lines, capacity, how='left', left_index=True, right_index=True).fillna(0)
            lines = lines[lines.capacity != 0]
            
        lines['line_width'] = self.scaling(lines['capacity'], 2, 30)

        # Plot transmission lines
        lines.plot(ax=ax, 
                   color=line_colour, 
                   linewidth=lines.line_width)
        
        plt.savefig(os.path.join(self.vis_results, f'line_capacity-{year}-{name}.png'))

    def plot_generators(self, lines=True):
        generators = self.generators.copy().to_crs('EPSG: 3347')

        if lines:
            lines = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'power_lines.feather')).to_crs('EPSG: 3347')
            line_colour = 'darkturquoise'
        fig, ax = self.create_base_map(USA=True, annotated=False)
        generators['node_size'] = self.scaling(generators['p_nom'], 100, 10000)

        if lines:
            # Plot transmission lines
            lines.plot(ax=ax, 
                    color=line_colour, 
                    linewidth=3,
                    alpha=0.75,
                    zorder=1)
            
        # Plot generator points
        generators.plot(ax=ax, 
                        color=generators['colour'], 
                        alpha=0.75,
                        markersize=generators['node_size'], 
                        edgecolor='black',
                        linewidth=1,
                        zorder=2)
        
        
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
        if lines:
            line_legend_elements = mlines.Line2D([], [], color=line_colour, linewidth=10, linestyle='-', label='Transmission')
            legend_elements = generator_legend_elements + [line_legend_elements]
        else:
            legend_elements = generator_legend_elements
        ax.legend(handles=legend_elements, fontsize=50, markerscale=1)
        
        # Saving plot
        if lines:
            plt.savefig(os.path.join(self.vis_results, 'full_map_Canada_w_lines.png'))
        else:
            plt.savefig(os.path.join(self.vis_results, 'full_map_Canada.png'))

    def plot_potentials(self, gen_type='PV'):
        if gen_type == 'PV':
            cmap = 'YlOrRd'
        elif gen_type == 'wind':
            cmap = 'BuPu'

        name = f'OPT_{gen_type}_average_cf'
        gridcells = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'filtered_gridcells.feather')).to_crs('EPSG: 3347')
        cf_data = pd.read_csv(os.path.join(self.path, 'results', f'{name}.csv'), index_col=0)
        gridcells = gridcells.join(cf_data)
        gridcells = gridcells[~gridcells[f'OPT_{gen_type}'].isna()]
        fig, ax = self.create_base_map(USA=True, annotated=False)
        
        gridcells.plot(ax=ax,
                    column=f'OPT_{gen_type}',
                    cmap=cmap,
                    edgecolor='black',
                    alpha=0.75)

        plt.savefig(os.path.join(self.vis_results, f'potential_mapping_{gen_type}.png'))

    def plot_industrial_loads(self):
        loads = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'industrial_loads.feather')).to_crs('EPSG: 3347')
        fig, ax = self.create_base_map(USA=True, annotated=False)
        loads['node_size'] = self.scaling(loads['load'], 100, 10000)

        loads.plot(ax=ax,
                   column='NAICS Code Description', 
                   cmap='tab20', 
                   markersize=loads['node_size'], 
                   legend=True, 
                   legend_kwds={'fontsize': 50, 'markerscale':9})

        plt.savefig(os.path.join(self.path, 'results', 'visualizations', 'industrial_loads_Canada.png'))

    def plot_hydro_basins(self):
        hydro_basins = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'river_basins.feather')).to_crs('EPSG: 3347')
        hydro_generators = self.generators.copy().to_crs('EPSG: 3347')
        hydro_generators = hydro_generators[hydro_generators.gen_type.str.contains('hydro')]

        fig, ax = self.create_base_map(USA=False, annotated=False)
        hydro_basins.plot(ax=ax)

        hydro_generators['node_size'] = self.scaling(hydro_generators['p_nom'], 100, 10000)
        hydro_generators.plot(ax=ax, 
                        color=hydro_generators['colour'], 
                        alpha=0.75,
                        markersize=hydro_generators['node_size'], 
                        edgecolor='black',
                        linewidth=1,
                        zorder=2)
        
        # Legend
        legend_elements = [
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
                        for gen_type, color in hydro_generators.groupby('gen_type')['colour'].first().items()
                        ]
        ax.legend(handles=legend_elements, fontsize=50, markerscale=1)
        plt.savefig(os.path.join(self.path, 'results', 'visualizations', 'hydro_basins_Canada.png'))

    def overview_vis(self, year):
        def normalize_direction(direction):
            start, end = direction.split('->')
            # Sort the two parts alphabetically so both directions become the same
            sorted_pair = sorted([start, end])
            return '->'.join(sorted_pair)
        
        lines = self.lines.copy().to_crs('EPSG: 3347')
        lines.loc[:, 'line'] = lines.start + '->' + lines.end
        lines.index = lines.line.apply(normalize_direction)

        results = self.results.copy()
        results = results[results.Time != 'All']
        results.loc[:, 'Time'] = results.Time.astype(int)
        results = results[results.Time == year]

        zones = self.zones.copy().to_crs('EPSG: 3347')
        zones.index = zones.cluster
        fig, ax = self.create_base_map(USA=True, annotated=False)

        ### Emissions
        emissions = results[results.Parameter == 'Emissions']
        emissions = emissions.groupby('Region')['Value'].sum()
        emissions.name = "emissions"
        zones = zones.merge(emissions, how='left', left_index=True, right_index=True).fillna(0)
        zones.loc[:, 'norm_emissions'] = zones.emissions.divide(zones.emissions.max())
        # Set min and max for colormap clipping (between 0 and 1)
        vmin = 0.2  # don't go lighter than 0.2
        vmax = 0.5  # don't go darker than 0.8

        # Create a Normalize instance that scales [vmin, vmax] -> [0,1]
        norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=True)
        cmap = plt.cm.Greys
        
        zones.plot(ax=ax, 
                   column='norm_emissions', 
                   cmap=cmap, 
                   #norm=norm, 
                   edgecolor='black', 
                   linewidth=1)

        ### Transmission        
        trans_capacity = results[results.Parameter == 'Transmission_Capacity']
        trans_capacity.loc[:, 'line'] = trans_capacity.Region.apply(normalize_direction)
        trans_capacity = trans_capacity.groupby('line')['Value'].max()

        trans_energy = results[results.Parameter == 'Line_Flow']
        trans_energy.loc[:, 'line'] = trans_energy.Region.apply(normalize_direction)
        trans_energy = trans_energy.groupby('line')['Value'].sum()

        utilization = pd.concat([trans_energy, trans_capacity.multiply(8760)], axis=1, join='inner')
        utilization.columns = ['Energy', 'Capacity']
        utilization['Value'] = utilization.Energy.divide(utilization.Capacity)
        utilization = utilization['Value']
        utilization.name = 'utilization'

        if year == '2021':
            # Scale from 0 to 1
            lines['capacity'] = lines[['capacity_fwd', 'capacity_bck']].max(axis=1)
        else:
            trans_capacity.name = 'capacity'
            lines = pd.merge(lines, trans_capacity, how='left', left_index=True, right_index=True).fillna(0)
            lines = lines[lines.capacity != 0]
        lines['line_width'] = self.scaling(lines['capacity'], 5, 50)
        
        lines = pd.merge(lines, utilization, how='left', left_index=True, right_index=True).fillna(0)
        cmap = plt.get_cmap('YlOrRd')
        # Map normalized values to colors
        lines['colour'] = lines['utilization'].apply(lambda x: colors.to_hex(cmap(x)))
        # Plot transmission lines
        lines.plot(ax=ax, 
                   color=lines.colour, 
                   linewidth=lines.line_width,
                   alpha=0.9,
                   zorder=1)
        
        ### Generation
        total_generation = results[results.Parameter == 'Annual_Generation']
        total_generation = total_generation.groupby(['Region'])['Value'].sum()
        total_generation = self.scaling(total_generation, 25000, 100000)

        gen_percent = results[results.Parameter == 'Annual_Generation_Mix']
        gen_percent.loc[:, 'Variable'] = gen_percent.Variable.replace(self.tech_map)
        gen_percent = gen_percent.groupby(['Region', 'Variable'])['Value'].sum().divide(100).unstack(level=1).fillna(0)
        
        # This draws a pie chart at position (x, y)
        def draw_pie(ax, ratios, X, Y, size, colors):
            start_angle = 0
            for ratio, color in zip(ratios, colors):
                angle = 360 * ratio
                wedge = plt.matplotlib.patches.Wedge((X, Y), 
                                                     size, 
                                                     start_angle, 
                                                     start_angle + angle, 
                                                     facecolor=color, 
                                                     lw=0.5, 
                                                     alpha=0.9, 
                                                     zorder=2
                                                     )
                ax.add_patch(wedge)
                start_angle += angle

        variables = list(self.tech_colors.keys())
        for idx, row in gen_percent.iterrows():
            geometry = zones.loc[idx, 'geometry'].centroid
            all_ratios = [row.get(var, 0) for var in variables]  # convert to fraction
           # Filter out zero ratios and corresponding variables/colors
            filtered = [(r, var) for r, var in zip(all_ratios, variables) if r > 0]
            ratios, vars_present = zip(*filtered)
            colours = [self.tech_colors[v] for v in vars_present]

            radius = total_generation.loc[idx]
            draw_pie(ax, ratios, geometry.x, geometry.y, radius, colours)

        plt.savefig(os.path.join(self.vis_results, f'overview_{year}.png'))

if __name__ == '__main__':
    vis = canada_visualizations()
    vis.plot_base()
    #vis.plot_prices(2021)
    #vis.plot_lines(2050, new=True)
    #vis.plot_lines(2050, new=False)
    #vis.plot_generators(lines=False)
    #vis.plot_potentials(gen_type='PV')
    #vis.plot_potentials(gen_type='wind')
    #vis.plot_industrial_loads()
    #vis.plot_hydro_basins()
    #vis.overview_vis(2021)