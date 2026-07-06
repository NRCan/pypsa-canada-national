# PyPSA-Canada-National

## Keywords
Python, Power Systems

## Project Description
`PyPSA-Canada-National` is an open source power system model for the 10 provinces of Canada. It is intended for use with the [pypsa_canada](https://github.com/NRCan/pypsa-canada) library. The model uses a variety of data sources to build an aggregated model 
of the Canadian bulk electricity system, for use with capacity expansion and planning models.

**Key Features:**
- **API-enabled data pipeline**: Pull all required data automatically through the use of API calls
- **Jupyter notebook format**: Allows for modifications and experimentation at each step of model creation

## Usage

### Overview
`PyPSA-Canada-National` provides a series of jupyter notebooks designed to walk the user through the model creation steps. These scripts should be run in order to generate the final pypsa formatted input files required for the pypsa_canada workflow.

### Basic Workflow
The workflow involves:
1. **Pre-Processing**: involves loading required data and building the initial data files used in future steps
2. **Network Clustering**: aggregating the spatial data into model regions
3. **VRE modeling, line distances and loads**: populates the model with loads, generation assets and transmission corridors
4. **Create Model**: formats the data into pypsa-readable .csv files

### Data Organization
- `data/`: Input data pulled from original sources is saved here
- `config/`: YAML configuration files defining model scenarios
- `results/`: Intermediate results from model creation are saved here along with the results of model runs

## Installation
### Environment
The notebooks in the 'PyPSA-Canada-National' repo are compatible with the [pypsa_canada](https://github.com/NRCan/pypsa-canada) python enivronment. Create a new environment and install the required packages by:

1. Create the virtual environment with either Conda or Python with Python 3.12

1-a) **For Anaconda/Miniconda users only, create a virtual environment with the following command:
```bash
$(base) conda create --name pypsa_cad_p312 python=3.12.10
```

1-b) **For Python users only, assuming you have a Python 3.12 installed, execute the following command to create a new virtual environment:
```bash
$(base) python -m venv pypsa_cad_p312
```
1-b) Proceed to activate the environment

2. Go into the pypsa_canada folder
```bash
(env)  >> cd [PROJECT_DIR]
```
3. Install the package/library:

```bash
(pypsa_cad_py312)  >> pip install -e .[dev]
```

#### PyArrow
Note that due to a conflict between the PyPAS-Canada library and the national model, the PyArrow package must be manually installed before running the notebooks. Notebook "4-Create Model" automatically uninstalls PyArrow when run. This issue will be resolved in future patches.

## Running the notebooks
The steps to build the 'PyPSA-Canada-National' model are provided in a series of jupyter notebooks. The individual cells of each notebook can be run using a compatible development environment, such as VSCode, or the entire notebook can be run as a python script.

## Data sources
Most data used in 'PyPSA-Canada-National' comes from the [CODERS](https://cme-emh.ca/en/coders/) database. Acesssing this data requires an account and API key. Once the API key has been obtained, create a text file in the data folder called "api_key.txt" with the api key pasted within.

## Licence
PyPSA MIT License : https://github.com/PyPSA/PyPSA/blob/master/LICENSE.txt
pypsa-eur License: https://github.com/PyPSA/pypsa-eur/tree/master/LICENSES

## Rights
Copyright CanmetENERGY - Varennes, NRCan, Goverment of Canada

## Authors
* Steven Wong (Natural Resources Canada - CanmetENERGY)
* Nathan De Matos (Natural Resources Canada - CanmetENERGY)
* Michel Bui (Natural Resources Canada - CanmetENERGY)
* Adrien Prigent (Natural Resources Canada - CanmetENERGY)
* Serban Ivanescu (Natural Resources Canada - CanmetENERGY)

## Contact Information
* Steven Wong (steven.wong@nrcan-rncan.gc.ca)
* Nathan De Matos (nathan.dematos@nrcan-rncan.gc.ca)
* Adrien Prigent (adrien.prigent@nrcan-rncan.gc.ca)
* Michel Bui (michel.bui@nrcan-rncan.gc.ca)
* Serban Ivanescu (serban.ivanescu@nrcan-rncan.gc.ca)

## Getting Further Information
https://docs.pypsa.org/latest/