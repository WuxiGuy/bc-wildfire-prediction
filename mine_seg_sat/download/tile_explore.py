import os
import sys
import json
import requests
import geopandas as gpd
from pathlib import Path
from pystac_client import Client

sys.path.append('/Users/glenn_hyh/Documents/github/bc-wildfire-prediction/mine_seg_sat')

from tile import generate_tiles
from utils.bands import get_band_specification
from stac import get_landsat2_data

# out_path = Path('/Users/glenn_hyh/Documents/github/bc-wildfire-prediction/datasets/S2B_10UCA_20230814_0_L2A/20230814')

# mine_gdf = gpd.read_file('/Users/glenn_hyh/Documents/github/bc-wildfire-prediction/shapefiles/campbell_river.shp')
# mine_gdf = mine_gdf.to_crs("EPSG:4326")
# start_date = "2023-08-01"
# end_date = "2023-08-30"
# print(f"Dropping {len(mine_gdf) - len(mine_gdf[mine_gdf.geometry.is_valid])} invalid geometries.")
# mine_gdf = mine_gdf[mine_gdf.geometry.is_valid]
# mine_aoi = mine_gdf[mine_gdf.geometry.is_valid].unary_union

# for file in out_path.iterdir():
#     band_name, window_size = get_band_specification(file)
#     if band_name == "B01":
#         break

# if band_name and window_size:
#     out_dir = file.parent / "tiles"
#     if not out_dir.exists():
#         out_dir.mkdir(parents=True)
#     generate_tiles(file, out_dir, band_name, window_size, mine_gdf)

# poly_obj = {
#     'type': 'Polygon',
#     'coordinates': [((-129.95406984011302, 47.611981504743426), (-129.95406984011302, 53.548857920619525), (-124.43221476016954, 53.548857920619525), (-124.43221476016954, 47.611981504743426), (-129.95406984011302, 47.611981504743426))]
# }
os.chdir('/Users/glenn_hyh/Documents/github/bc-wildfire-prediction')
# client_id = os.environ.get('CLIENT_ID')
# client_secret = os.environ.get('CLIENT_SECRET')
# auth_token_url = os.environ.get('AUTH_TOKEN_URL')

# # update the api url by setting the environment variable
# api_url = os.environ.get('API_URL')
# # api_url = "https://api.eds.earthdaily.com/archive/v1/stac/v1"


# def get_new_token():
#     token_req_payload = {'grant_type': 'client_credentials'}
#     token_response = requests.post(auth_token_url,
#     data=token_req_payload, verify=False, allow_redirects=False,
#     auth=(client_id, client_secret))
#     token_response.raise_for_status()

#     tokens = json.loads(token_response.text)
#     return tokens['access_token']


# token = get_new_token()
# client = Client.open(api_url, headers={ "Authorization": f"Bearer {token}" })
# start_date = "2023-08-01"
# end_date = "2023-08-30"

# items, tile_gdf = get_landsat2_data(client, poly_obj, start_date, end_date)


href = "https://landsatlook.usgs.gov/data/collection02/level-2/standard/oli-tirs/2023/048/026/LC08_L2SP_048026_20230814_20230819_02_T1/LC08_L2SP_048026_20230814_20230819_02_T1_ST_QA.TIF"
outpath = "datasets/landsat2/LC08_L2SP_048026_20230814_20230819_02_T1_ST/20230814/QA_ST.tif"
headers = {'Authorization': 'Bearer ' + usgs_token}

with requests.get(href, stream=True, headers=headers) as r:
    r.raise_for_status()
    with open(outpath, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
