import io
import json
import os
import tempfile
import zipfile
from urllib.request import urlopen

import geopandas as gpd
import pandas as pd
import requests
from shapely import LineString, Point


def CODERS_pull(request, key, url=None, type="json"):
    if url == None:
        with urlopen(f"https://api.sesit.ca/{request}?key={key}") as response:
            response_content = response.read()
    else:
        with urlopen(f"https://api.sesit.ca/{request}?{url}&key={key}") as response:
            response_content = response.read()
    if type == "json":
        json_response = json.loads(response_content)
        df = pd.json_normalize(json_response)
    elif type == "csv":
        df = pd.read_csv(io.BytesIO(response_content))
    return df


def download_file(url: str, output_path: str):
    output_path = os.path.abspath(output_path)
    if os.path.isfile(output_path):
        print(f"{output_path} already exists. Skipping download.")
        return

    temporary_path = None
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"Downloading {url}...")
        with requests.get(url, stream=True, timeout=(10, 120)) as response:
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=os.path.dirname(output_path),
                suffix=".part",
                delete=False,
            ) as file:
                temporary_path = file.name
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

        if os.path.getsize(temporary_path) == 0:
            raise OSError("The downloaded file is empty.")

        os.replace(temporary_path, output_path)
        temporary_path = None
        print(f"Download complete: {output_path}")
    except (requests.RequestException, OSError) as exc:
        message = (
            f"Download failed: {exc}\n"
            f"Download the file manually from:\n{url}\n"
            f"Save it as:\n{output_path}\n"
            "Then rerun this cell."
        )
        print(message)
        raise RuntimeError(message) from exc
    finally:
        if temporary_path is not None:
            os.remove(temporary_path)


def unzip(output_path: str, extract_to: str):
    if extract_to is None:
        return

    if not os.path.isfile(output_path):
        raise FileNotFoundError(
            f"Archive missing: {output_path}. "
            "Download it manually into this location and rerun the cell."
        )
    if not zipfile.is_zipfile(output_path):
        raise zipfile.BadZipFile(
            f"{output_path} is not a valid ZIP file. "
            "Replace it with a manually downloaded ZIP and rerun the cell."
        )

    print(f"Extracting {output_path}...")
    try:
        os.makedirs(extract_to, exist_ok=True)
        with zipfile.ZipFile(output_path, "r") as archive:
            archive.extractall(extract_to)
    except (OSError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as exc:
        raise RuntimeError(
            f"Extraction failed for {output_path}: {exc}. "
            f"Extract it manually into {os.path.abspath(extract_to)}."
        ) from exc
    print(f"Extracted to {extract_to}")


def download_and_unzip(url: str, output_path: str, extract_to: str):
    download_file(url, output_path)
    unzip(output_path, extract_to)


# Function to create geopandas dataframe of points at each node
def mapPoints(data):  # given a dataframe with one set of lon/lat co-ords
    geometry = [Point(xy) for xy in zip(data["longitude"], data["latitude"])]
    geo_df = gpd.GeoDataFrame(
        data, crs={"init": "EPSG:4326"}, geometry=geometry
    ).to_crs("EPSG:4326")
    return geo_df


# Function to create geopandas dataframe with lines between nodes,
def mapLines(data):  # given a dataframe with 2 sets of lon/lat co-ords
    geometry = [LineString(xy) for xy in zip(data.geometry_1, data.geometry_2)]
    geo_df = gpd.GeoDataFrame(data, crs={"init": "EPSG:4326"}, geometry=geometry)
    return geo_df  # returns a geopandas dataframe with the line geometries assigned


def read_api_key(path):
    with open(os.path.join(path, "api_key.txt"), "r") as file:
        return file.read()
