from ..lib import check_types, save_bbox
import numpy as np
import pandas as pd
import os
import glob
from sentinelhub import BBox, CRS
from typing import List

def unpack_ras(ras_path: str, outdir:str, timestamps: List[str], img_w: int, img_h: int):
    with open(ras_path, "r") as rasfile:
        ras = np.fromfile(rasfile, dtype=np.int16)

        n = len(timestamps)
        img_len = img_w*img_h
        for i in range(n):
            print(f"Saving image {i+1}/{n}", end='\r')
            img = ras[i*img_len:(i+1)*img_len].reshape(img_w,img_h)

            # Save as .npy
            ts = timestamps[i]
            np.save(os.path.join(outdir, ts + '.npy'), img)

@check_types
# Get all necessary info from RHD file
def get_rhd_info(rhd_path: str, crs: CRS = CRS('32630')):
    # Read the RHD file
    with open(rhd_path, "r") as rhdfile:
        rhd = rhdfile.readlines()
        # Get image dimensions from 3rd line
        try:
            dims = [int(i) for i in rhd[2].strip().split(" ") if i.isdigit()]
            img_h, img_w = dims
        except:
            raise ValueError(f"Could not get image dimensions from {rhd_path}")

        # Get the bounding box from the 4th line
        try:
            fields = [float(i) for i in rhd[3].strip().split(" ") if i != ""]
            resolution = fields[0]
            xmin = fields[1]
            ymin = fields[2]
            bbox = BBox([xmin, ymin, xmin + img_w*resolution, ymin + img_h*resolution], crs=crs)
        except:
            raise ValueError(f"Could not get bounding box from {rhd_path}")

        # Get timestamps from 5+ lines
        try:
            lines = rhd[5:]

            # Trip left and right whitespaces
            lines = [line.strip() for line in lines]

            # Split by whitespaces
            lines = [line.split() for line in lines]

            # Convert to dataframe
            times_df = pd.DataFrame(lines)

            # Join first 3 columns to one datetime string
            times_df["datetime"] = pd.to_datetime(times_df[1] + '_' + times_df[2] + '_' + times_df[3], format='%Y_%m_%d')

            # Get datetimes
            timestamps = times_df.datetime.dt.strftime(date_format='%Y_%m_%d').values.tolist()
        except:
            raise ValueError(f"Could not get timestamps from {rhd_path}")
        
    return img_h, img_w, timestamps, bbox

@check_types
def unpack_vista_unzipped(ras_path: str, rhd_path:str, outdir:str, delete_after:bool = False, crs:CRS = CRS('32630')):
    # Create output directory
    os.makedirs(outdir, exist_ok=True)
   
    # Get image dimensions and timestamps from RHD
    img_h, img_w, timestamps, bbox = get_rhd_info(rhd_path, crs=crs)

    # Save bbox separately 
    bbox_path = os.path.join(outdir, 'bbox.pkl')
    save_bbox(bbox, bbox_path)

    # Unpack all images from ras file and save as .npy files
    print(f"Unpacking {len(timestamps)} images from {ras_path}")
    unpack_ras(ras_path, outdir, timestamps, img_w, img_h)

    # Delete RAS and RHD files
    if delete_after:
        print(f"Deleting {ras_path} and {rhd_path}")
        os.remove(ras_path)
        os.remove(rhd_path)

@check_types    
def unpack_vista(datadir: str, bands: list = ['B2', 'B3', 'B4', 'B8A'], delete_ras:bool = True):
    # Check if all bands are present
    for band in bands:
        if not os.path.exists(os.path.join(datadir, f"{band}.zip")):
            raise FileNotFoundError(f"Band {band} missing in {datadir}")
        
    for band in bands:
        # Skip if already unzipped
        if os.path.exists(os.path.join(datadir, band)):
            print(f"Band {band} already unzipped")
        else:
            # Unzip band
            print(f"Unzipping {band}")
            os.system(f"unzip {os.path.join(datadir, f'{band}.zip')} -d {os.path.join(datadir, band)}")

        # Unpack all RAS files
        ras_paths = glob.glob(os.ath.join(datadir, band, "*.RAS"))
        for ras_path in ras_paths:
            # Check if RHD variant also exists
            rhd_path = ras_path.replace('.RAS', '.RHD')
            if not os.path.exists(rhd_path):
                raise FileNotFoundError(f"RHD file {rhd_path} not found")
            unpack_vista_unzipped(ras_path, rhd_path, delete_after=delete_ras)

@check_types
def get_scl_from_lai(lai_path: str):
    lai = np.load(lai_path)
    return (lai > 0)[np.newaxis, ..., np.newaxis]



