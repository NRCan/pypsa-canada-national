import pandas as pd
import os
import matplotlib.pyplot as plt

def compare_hydro_ror_station():
    path = os.getcwd()
    station = 'Saunders'
    unscaled_cf = pd.read_csv(os.path.join(path, 'results', 'testing', 'unscaled_ror_cf.csv'), index_col=0)
    unscaled_cf = unscaled_cf.divide(unscaled_cf.max())
    unscaled_cf = unscaled_cf[station]
    unscaled_cf.name = 'Unscaled'

    cf = pd.read_csv(os.path.join(path, 'results', 'ror_hydro_cf.csv'), index_col=0)
    cf = cf[station]
    cf.name = 'Scaled'
    cf = pd.DataFrame(cf).merge(unscaled_cf, left_index=True, right_index=True)
    cf.index = pd.to_datetime(cf.index)
    cf = cf.loc['2021-05-01':'2021-06-01']

    fig, ax = plt.subplots()
    cf.Unscaled.plot(ax=ax)
    cf.Scaled.plot(ax=ax)
    ax.set_title(f'{station}: Annual Capacity Factor')
    #ax.set_ylabel('Demand [MWh]')
    fig.tight_layout()
    plt.savefig(os.path.join(path, 'results', 'visualizations', f'hydro_compare_{station}.png'))

def plot_inflows(station):
    path = os.getcwd()
    inflows = pd.read_csv(os.path.join(path, 'results', 'hydro_inflows.csv'), index_col=0)
    inflows = inflows[station]

    fig, ax = plt.subplots()
    inflows.plot(ax=ax)
    ax.set_title(f'{station}: Hourly Inflows')
    ax.set_ylabel('Inflow [MWh]')
    fig.tight_layout()
    plt.savefig(os.path.join(path, 'results', 'visualizations', f'{station}_inflows.png'))

def plot_loads():
    path = os.getcwd()
    loads = pd.read_csv(os.path.join(path, 'results', 'pypsa_model', 'loads-p_set.csv'), index_col=0)

    # Load profiles
    qc_profiles = loads.loc[:, loads.columns.str.contains('QC')]
    qc_profiles['total_load'] = qc_profiles.sum(axis=1)
    qc_profiles['day'] = (qc_profiles.index // 24) - 364
    qc_profiles = qc_profiles.groupby('day')['total_load'].sum()
    fig, ax = plt.subplots()
    qc_profiles.plot(ax=ax)
    ax.set_ylabel('Demand [MWh]')
    fig.tight_layout()
    plt.savefig(os.path.join(path, 'results', 'visualizations', f'qc_load_profile.png'))

    qc_profiles = loads[['QC_Central_ind_load', 'QC_Central_pop_load', 'QC_South_ind_load', 'QC_South_pop_load']]
    qc_profiles['QC_Central_load'] = qc_profiles.QC_Central_ind_load + qc_profiles.QC_Central_pop_load
    qc_profiles['QC_South_load'] = qc_profiles.QC_South_ind_load + qc_profiles.QC_South_pop_load
    qc_profiles = qc_profiles[['QC_Central_load', 'QC_South_load']]
    qc_profiles['day'] = (qc_profiles.index // 24) - 364
    qc_profiles = qc_profiles.groupby('day').sum()
    fig, ax = plt.subplots()
    qc_profiles.plot(ax=ax)
    ax.set_ylabel('Demand [MWh]')
    fig.tight_layout()
    plt.savefig(os.path.join(path, 'results', 'visualizations', f'qc_south_central_load_profile.png'))

    # Regional loads
    loads = pd.DataFrame(loads.sum(axis=0), columns=['load'])
    loads['province'] = loads.index.str[:2]
    loads['type'] = loads.index.str.split('_').str[-2]
    loads['Region'] = loads.index.str.split('_pop_load').str[0]
    loads.loc[loads.Region.str.contains('ind'), 'Region'] = loads[loads.Region.str.contains('ind')].index.str.split('_ind_load').str[0]
    loads = loads.reset_index()
    loads = loads.drop(['index', 'province'], axis=1).pivot(index='Region', columns='type', values='load').fillna(0)
    loads['total_load'] = loads['ind'] + loads['pop']
    loads = loads.rename(columns={'ind':'industrial_load', 'pop':'population_load'})

    fig, ax = plt.subplots()
    loads.plot.bar(ax=ax)
    ax.set_ylabel('Demand [MWh]')
    fig.tight_layout()
    plt.savefig(os.path.join(path, 'results', 'visualizations', f'load_bar_plot.png'))
    
if __name__ == '__main__':
    #compare_hydro_ror_station()
    plot_inflows('Mactaquac')
