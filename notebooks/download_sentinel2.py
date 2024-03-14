import os
import json
import requests
from pathlib import Path
import sys
from datetime import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from pystac_client import Client
from pystac.item import Item
from shapely.geometry import Polygon
from shapely.prepared import prep

project_path = os.environ.get('PROJECT_PATH')
sys.path.append(project_path)
from mine_seg_sat.download.stac import (
    get_sentinel2_data,
    remove_small_tiles,
    add_geometries_iteratively,
    download_files_for_item
)
from mine_seg_sat.utils.bands import get_band_specification
from mine_seg_sat.constants import EXTRACTED_BANDS
from mine_seg_sat.download.tile import generate_tiles

# load_dotenv()

# turn off load_dotenv() if you want to use the .env file

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
auth_token_url = os.environ.get('AUTH_TOKEN_URL')

# update the api url by setting the environment variable
api_url = os.environ.get('API_URL')
# api_url = "https://api.eds.earthdaily.com/archive/v1/stac/v1"


def get_new_token():
    token_req_payload = {'grant_type': 'client_credentials'}
    token_response = requests.post(auth_token_url,
    data=token_req_payload, verify=False, allow_redirects=False,
    auth=(client_id, client_secret))
    token_response.raise_for_status()

    tokens = json.loads(token_response.text)
    return tokens['access_token']

def load_canada_map() -> gpd.GeoDataFrame:
    # CRS is EPSG:4326
    gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    return gdf[gdf.name == "Canada"]

def grid_bounds(geom, delta):
    # Convert a larger shapefile into grids...
    # Logic retrieved from:
    # https://www.matecdev.com/posts/shapely-polygon-gridding.html
    minx, miny, maxx, maxy = geom.bounds
    nx = int((maxx - minx)/delta)
    ny = int((maxy - miny)/delta)
    gx, gy = np.linspace(minx,maxx,nx), np.linspace(miny,maxy,ny)
    grid = []
    for i in range(len(gx)-1):
        for j in range(len(gy)-1):
            poly_ij = Polygon([[gx[i],gy[j]],[gx[i],gy[j+1]],[gx[i+1],gy[j+1]],[gx[i+1],gy[j]]])
            grid.append(poly_ij)

    return grid


def partition(geom, delta):
    prepared_geom = prep(geom)
    grid = list(filter(prepared_geom.intersects, grid_bounds(geom, delta)))
    return grid

def get_intersecting_polygons(polygons, mine_aoi):
    """
    Given an area with larger multipolygons, and a group of polygons return a list of
    polygons that intersect with the area of interest.
    """
    intersecting_polygons = []
    for polygon in polygons:
        if mine_aoi.intersects(polygon):
            intersecting_polygons.append(polygon)
    return intersecting_polygons

def get_all_overlapping_tiles(polygons, start_date, end_date):
    print(f"Getting area for: {len(polygons)} polygons")
    all_items, all_gdfs = [], []
    for polygon in polygons:
        poly_obj = {
            "type": "Polygon",
            "coordinates": list(polygon.__geo_interface__["coordinates"])
        }
        items, tile_gdf = get_sentinel2_data(client, poly_obj, start_date, end_date)
        if len(items) == 0:
            print("No items found for given area... Not great.")
            continue


        tile_gdf = remove_small_tiles(tile_gdf, reproject=True)
        _, tile_gdf = add_geometries_iteratively(tile_gdf)

        wanted_gdf = tile_gdf[tile_gdf.intersects(mine_aoi)]

        wanted_tiles = [name.split("/")[-1] for name in wanted_gdf["earthsearch:s3_path"].tolist()]
        wanted_items = [item for item in items if item.id in wanted_tiles]
        all_items.append(wanted_items)
        all_gdfs.append(wanted_gdf)

    return all_items, all_gdfs

def download_and_tile_files(gdf: gpd.GeoDataFrame, items: list[Item], aoi_gdf: gpd.GeoDataFrame, output_dir: Path):

    gdf["downloaded"] = False
    for tile in items:
        dt_obj = datetime.strptime(tile.properties["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_date = dt_obj.strftime('%Y%m%d')
        out_path = output_dir / tile.id / formatted_date
        print(f"Downloading files for {tile.id} to {out_path}")
        downloaded = download_files_for_item(tile, all_download_files, out_path)

        if downloaded:
            gdf.loc[
                gdf["s2:granule_id"] == tile.properties["s2:granule_id"], "downloaded"
            ] = True
            for file in out_path.iterdir():
                band_name, window_size = get_band_specification(file)
                if band_name and window_size:
                    out_dir = file.parent / "tiles"
                    if not out_dir.exists():
                        out_dir.mkdir(parents=True)
                    generate_tiles(file, out_dir, band_name, window_size, aoi_gdf)

    print(f"Downloaded: {len(gdf[gdf['downloaded'] == True])} / {len(gdf)} files. {len(gdf[gdf['downloaded'] == False])} failed to download.")

token = get_new_token()
print(f"Token: {token}")
client = Client.open(api_url, headers={ "Authorization": f"Bearer {token}" })

areas_geojson = load_canada_map()
areas_geojson.iloc[0].geometry

polygons = partition(areas_geojson.iloc[0].geometry, 5)

#data_list = ["2022-07-21", "2022-07-26"], ["2022-07-30", "2022-08-02"], ["2022-08-08", "2022-08-19"],
#            ["2022-08-22", "2022-09-10"], ["2022-09-11", "2022-09-23"],

date_list = [["2022-06-27", "2022-06-30"],
            ["2022-07-13", "2022-07-15"], 
            ["2022-07-21", "2022-07-26"], ["2022-07-30", "2022-08-02"], ["2022-08-08", "2022-08-19"],
            ["2022-08-22", "2022-09-10"], ["2022-09-11", "2022-09-23"], ["2022-09-25", "2022-10-10"],
            ["2022-10-12", "2022-10-24"], ["2022-11-15", "2022-11-20"]]


high_resolution_bands = {"red": "B04", "green": "B03", "blue": "B02", "nir": "B08"}
mid_resolution_bands = {"rededge1": "B05", "rededge2": "B06", "rededge3": "B07", "nir08": "B8A", "swir16": "B11", "swir22": "B12"}
low_resolution_bands = {"coastal": "B01", "nir09": "B09"}

other_files = {
    "scl": "scl", # Scene Classification Map
    "aot": "aot", # Aerosol Optical Thickness
    "tileinfo_metadata": "metadata" # Tile Metadata
}

all_download_files = {**high_resolution_bands, **mid_resolution_bands, **low_resolution_bands, **other_files}

# Obtain mine shapefile from
'''
Where to get shapefiles
'''
# mine_gdf = gpd.read_file('../shapefiles/around_kelowna/around_kelowna.shp')
for start_date, end_date in date_list:
    print("--------------------")
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
    print("--------------------")
    mine_gdf = gpd.read_file('../shapefiles/campbell_river.shp')
    mine_gdf = mine_gdf.to_crs("EPSG:4326")
    print(f"Dropping {len(mine_gdf) - len(mine_gdf[mine_gdf.geometry.is_valid])} invalid geometries.")
    mine_gdf = mine_gdf[mine_gdf.geometry.is_valid]
    mine_aoi = mine_gdf[mine_gdf.geometry.is_valid].unary_union

    wanted_polygons = get_intersecting_polygons(polygons, mine_aoi)
    print(f"Number of intersecting polygons: {len(wanted_polygons)}")
    print(f"Number of polygons: {len(polygons)}")

    all_items, all_gdfs = get_all_overlapping_tiles(wanted_polygons, start_date, end_date)

    items = [item for sublist in all_items for item in sublist] # covers western canada
    gdfs = pd.concat(all_gdfs)
    print(f"Number of items: {len(items)}")
    print(f"Number of gdfs: {len(gdfs)}")

    output_dir = Path("../datasets/sentinel2")
    download_and_tile_files(gdfs, items, mine_gdf, output_dir)
