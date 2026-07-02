import geopandas as gpd
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.colors import ListedColormap

class canada_visualizations():
    def __init__(self, scenario_name):
        self.path = os.getcwd()
        self.results_path = Path(r"C:\Users\ndematos\Downloads\reference-custom-OPT_VRE_HYDRO-20-202508152108-0\reference-custom-OPT_VRE_HYDRO-20-202508152108-0\Output")
        self.vis_results = os.path.join(self.path, 'results', 'visualizations', scenario_name)

        if not os.path.exists(self.vis_results):
            os.mkdir(self.vis_results)
        
        # Read data
        zones = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'clustered_zone_data.feather')).reset_index()
        self.zones = gpd.GeoDataFrame(zones, geometry=zones.geometry, crs='EPSG: 4326').rename(columns={'index':'cluster'})
        lines = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'cluster_interfaces.feather'))
        self.lines = gpd.GeoDataFrame(lines, geometry=lines.geometry, crs='EPSG: 4326')
        nodes = gpd.read_feather(os.path.join(self.path, 'results', 'node_data.feather'))
        self.nodes = gpd.GeoDataFrame(nodes, geometry=nodes.geometry, crs='EPSG: 4326')
        generators = gpd.read_feather(os.path.join(self.path, 'results', 'visualization_data', 'generator_data.feather'))
        self.generators = gpd.GeoDataFrame(generators, geometry=generators.geometry, crs='EPSG: 4326')

        self.gen_type_map = {
            'coal_IGCC': 'Coal',
            'default_biogas': 'Biomass',
            'default_biomass': 'Biomass',
            'default_diesel': 'Diesel',
            'default_liion_battery':'Li-ion battery',
            'default_nuclear': 'Nuclear',
            'default_oil': 'Oil',
            'default_solar_PV': 'Solar PV',
            'gas_CC': 'Natural Gas',
            'gas_CT': 'Natural Gas',
            'hydro_ror': 'Hydro',
            'hydro_storage': 'Hydro',
            'wind_2021': 'Onshore Wind',
            'wind_new': 'Onshore Wind'
        }

        results = pd.read_csv(os.path.join(self.results_path, "reference-custom-OPT_VRE_HYDRO-20-202508152108_results_summary_default.csv"))
        results.loc[:, 'Variable'] = results.loc[:, 'Variable'].replace(self.gen_type_map)
        self.results = results
    
    def stacked_bar_plot(self, parameters, grouping, xlabel, ylabel, title):
        df = self.results.copy()
        df = df[df.Parameter.isin(parameters)]
        df = df.groupby(grouping)['Value'].sum()
        df = df.unstack(level=0).fillna(0)

        fig, ax = plt.subplots(figsize=(10,5))
        df.plot(ax=ax, kind='bar', stacked=True)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self.vis_results, f'{title} Bar.png'))

    def line_plot(self, parameters, grouping, xlabel, ylabel, title):
        df = self.results.copy()
        df = df[df.Parameter.isin(parameters)]
        df = df.groupby(grouping)['Value'].sum()
        df = df.unstack(level=0).fillna(0)

        fig, ax = plt.subplots(figsize=(10,5))
        df.plot(ax=ax, kind='line')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self.vis_results, f'{title} Line.png'))

if __name__ == '__main__':
    vis = canada_visualizations('Testing')
    # vis.stacked_bar_plot(
    #     ['Capital_Cost', 'Fixed_OM_Cost', 'Fuel_Cost', 'Variable_Cost', 'Carbon_Cost'],
    #     ['Parameter', 'Time'],
    #     'Year',
    #     '$',
    #     'Total System Cost'
    #     )
    # vis.stacked_bar_plot(
    #     ['New_Capacity'],
    #     ['Variable', 'Time'],
    #     'Year',
    #     'Capacity [MW]',
    #     'New Installed Capacity'
    #     )
    vis.stacked_bar_plot(
        ['Emissions'],
        ['Variable', 'Time'],
        'Year',
        'TCO2eq',
        'Emissions'
    )
    vis.line_plot(
        ['Emissions'],
        ['Parameter', 'Time'],
        'Year',
        'TCO2eq',
        'Emissions'
    )