# <a id="english"></a>PyPSA-Canada-National

[English](#english) | [Français](#french)

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
The notebooks in the 'PyPSA-Canada-National' repo are compatible with the [pypsa_canada](https://github.com/NRCan/pypsa-canada) python environment. Create a new environment and install the required packages by:

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

---

# <a id="french"></a>PyPSA-Canada-National (Français)

[English](#english) | [Français](#french)

## Mots-clés
Python, Systèmes électriques

## Description du projet
`PyPSA-Canada-National` est un modèle open source de système électrique pour les 10 provinces du Canada. Il est conçu pour être utilisé avec la bibliothèque [pypsa_canada](https://github.com/NRCan/pypsa-canada). Le modèle utilise diverses sources de données pour construire un modèle agrégé du réseau électrique canadien à grande échelle, destiné aux modèles de planification et d'expansion des capacités.

**Fonctionnalités clés :**
- **Pipeline de données activé par API** : Récupère automatiquement toutes les données requises à l'aide d'appels API
- **Format notebook Jupyter** : Permet des modifications et de l'expérimentation à chaque étape de création du modèle

## Utilisation

### Vue d'ensemble
`PyPSA-Canada-National` fournit une série de notebooks Jupyter conçus pour guider l'utilisateur à travers les étapes de création du modèle. Ces scripts doivent être exécutés dans l'ordre afin de générer les fichiers d'entrée finaux au format pypsa requis pour le workflow pypsa_canada.

### Workflow de base
Le workflow comprend :
1. **Pré-traitement** : charger les données requises et construire les fichiers de données initiaux utilisés aux étapes suivantes
2. **Clustering du réseau** : agréger les données spatiales en régions de modèle
3. **Modélisation ENR, distances de lignes et charges** : alimenter le modèle avec les charges, les actifs de production et les corridors de transmission
4. **Create Model** : formater les données en fichiers `.csv` lisibles par pypsa

### Organisation des données
- `data/` : les données d'entrée récupérées depuis les sources d'origine y sont enregistrées
- `config/` : fichiers de configuration YAML définissant les scénarios de modèle
- `results/` : résultats intermédiaires de la création du modèle, ainsi que les résultats des exécutions du modèle

## Installation
### Environnement
Les notebooks du dépôt 'PyPSA-Canada-National' sont compatibles avec l'environnement Python [pypsa_canada](https://github.com/NRCan/pypsa-canada). Créez un nouvel environnement puis installez les packages requis :

1. Créez l'environnement virtuel avec Conda ou Python 3.12

1-a) **Pour les utilisateurs Anaconda/Miniconda uniquement, créez un environnement virtuel avec la commande suivante :
```bash
$(base) conda create --name pypsa_cad_p312 python=3.12.10
```

1-b) **Pour les utilisateurs Python uniquement, en supposant que Python 3.12 est installé, exécutez la commande suivante pour créer un nouvel environnement virtuel :
```bash
$(base) python -m venv pypsa_cad_p312
```
1-b) Poursuivez en activant l'environnement

2. Entrez dans le dossier pypsa_canada
```bash
(env)  >> cd [PROJECT_DIR]
```
3. Installez le package/la bibliothèque :

```bash
(pypsa_cad_py312)  >> pip install -e .[dev]
```

#### PyArrow
Notez qu'en raison d'un conflit entre la bibliothèque PyPAS-Canada et le modèle national, le package PyArrow doit être installé manuellement avant d'exécuter les notebooks. Le notebook "4-Create Model" désinstalle automatiquement PyArrow lors de son exécution. Ce problème sera corrigé dans de futurs correctifs.

## Exécution des notebooks
Les étapes pour construire le modèle 'PyPSA-Canada-National' sont fournies dans une série de notebooks Jupyter. Les cellules individuelles de chaque notebook peuvent être exécutées avec un environnement de développement compatible, tel que VSCode, ou le notebook entier peut être exécuté en tant que script Python.

## Sources de données
La plupart des données utilisées dans 'PyPSA-Canada-National' proviennent de la base de données [CODERS](https://cme-emh.ca/en/coders/). L'accès à ces données nécessite un compte et une clé API. Une fois la clé API obtenue, créez un fichier texte dans le dossier data nommé "api_key.txt" et collez-y la clé API.

## Licence
Licence MIT PyPSA : https://github.com/PyPSA/PyPSA/blob/master/LICENSE.txt
Licence pypsa-eur : https://github.com/PyPSA/pypsa-eur/tree/master/LICENSES

## Droits
Copyright CanmetENERGY - Varennes, RNCan, Gouvernement du Canada

## Auteurs
* Steven Wong (Ressources naturelles Canada - CanmetENERGY)
* Nathan De Matos (Ressources naturelles Canada - CanmetENERGY)
* Michel Bui (Ressources naturelles Canada - CanmetENERGY)
* Adrien Prigent (Ressources naturelles Canada - CanmetENERGY)
* Serban Ivanescu (Ressources naturelles Canada - CanmetENERGY)

## Informations de contact
* Steven Wong (steven.wong@nrcan-rncan.gc.ca)
* Nathan De Matos (nathan.dematos@nrcan-rncan.gc.ca)
* Adrien Prigent (adrien.prigent@nrcan-rncan.gc.ca)
* Michel Bui (michel.bui@nrcan-rncan.gc.ca)
* Serban Ivanescu (serban.ivanescu@nrcan-rncan.gc.ca)

## Informations complémentaires
https://docs.pypsa.org/latest/