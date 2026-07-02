from urllib.request import urlopen
import pandas as pd
import geopandas as gpd
import json
import requests
import zipfile
import os
from shapely import Point, LineString
import io

def CODERS_pull(request, key, url=None, type='json'):
    if url == None:
        with urlopen(f'https://api.sesit.ca/{request}?key={key}') as response:
            response_content = response.read()
    else:
        with urlopen(f'https://api.sesit.ca/{request}?{url}&key={key}') as response:
            response_content = response.read()
    if type == 'json':
        json_response = json.loads(response_content)
        df = pd.json_normalize(json_response)
    elif type == 'csv':
        df = pd.read_csv(io.BytesIO(response_content))
    return df

def download_and_unzip(url:str, output_path:str, extract_to:str):
    # Check if file already exists
    if os.path.exists(output_path):
        print(f"{output_path} already exists. Skipping download.")
        return
    else:
        print(f"Downloading {url}...")
        response = requests.get(url, stream=True)

        with open(output_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("Download complete")

    # Unzip the file
    if extract_to != None:
        if zipfile.is_zipfile(output_path):
            print(f"Extracting {output_path}...")
            with zipfile.ZipFile(output_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"Extracted to {extract_to}/")
        if os.path.exists(output_path):
            os.remove(output_path)
        else:
            print(f"{output_path} is not a valid zip file")

# Function to create geopandas dataframe of points at each node
def mapPoints(data): #given a dataframe with one set of lon/lat co-ords
    geometry = [Point(xy) for xy in zip(data['longitude'], data['latitude'])]
    geo_df = gpd.GeoDataFrame(data, crs = {'init':'EPSG:4326'}, geometry = geometry).to_crs('EPSG: 4326')
    return geo_df

# Function to create geopandas dataframe with lines between nodes,
def mapLines(data):  #given a dataframe with 2 sets of lon/lat co-ords
    geometry = [LineString(xy) for xy in zip(data.geometry_1, data.geometry_2)]
    geo_df = gpd.GeoDataFrame(data, crs = {'init':'EPSG:4326'}, geometry = geometry)
    return geo_df #returns a geopandas dataframe with the line geometries assigned

def read_api_key(path):
    with open(os.path.join(path, 'api_key.txt'), 'r') as file:
        return file.read()