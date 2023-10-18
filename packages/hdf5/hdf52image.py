
'''
Usage : python3 hdf52image.py -o <image path> -i <input hdf5 file path with filename>
ex) python3 hdf52image.py -o ./ -i /mnt/smb_ssd/out.hdf5
'''

import h5py
import argparse
import sys
import os
import io
import glob
from PIL import Image
import numpy as np
from pathlib import Path
import time
import cv2

group_name = "dataset"

class TransformExeption(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

# extract path
data_path = []
group_path = []
def extract(name, obj):
    if isinstance(obj, h5py.Dataset):
        data_path.append(name)
    elif isinstance(obj, h5py.Group):
        group_path.append(name)

def hdf52image(infile, outpath):
    try:

        print("Elapsed Time Performance(sec) : ", time.time()-s_time)

    except TransformExeption as e:
        print("Error : ",e)


if __name__ == "__main__":
    #arguments
    parser = argparse.ArgumentParser(description="hdf52image --o out_path -i hdf5_file")
    parser.add_argument('-o', nargs='?', required=True, help="output path")
    parser.add_argument('-i', nargs='?', required=True, help="Input HDF5 file")
    args = parser.parse_args()

    _out_path = args.o
    _in_hdf5 = args.i

    _base_dir = os.path.dirname(os.path.abspath(__file__)) 
    s_time = time.time()
    with h5py.File(_in_hdf5, "r") as hf:
        hf.visititems(extract)

        for path in data_path:
            abs_path = Path(_base_dir)/Path(path)
            dir= os.path.dirname(abs_path)

            if not os.path.exists(dir):
                os.makedirs(dir)

            # with opencv
            #img_data = np.fromstring(np.array(hf[path]), dtype = np.uint8)
            #img_encoded = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

            # with pillow
            img_data = Image.open(io.BytesIO(np.array(hf[path])))
            img_data.save(abs_path, "png")
            print("extracted ", abs_path)

        hf.close()
    print("Elapsed Time Performance(sec) : ", time.time()-s_time)


    