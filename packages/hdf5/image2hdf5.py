
'''
Usage : python3 image2hdf5.py -i <image path> -o <output hdf5 file path with filename>
ex) python3 image2hdf5.py -i ./cam1_images/ -o /mnt/smb_ssd/out.hdf5
'''
import h5py
import argparse
import sys
import os
import glob
from PIL import Image
import numpy as np
import time

group_name = "dataset"

class TransformExeption(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

# png file to hdf5
def image2hdfs(inpath, outfile):
    try:
        s_time = time.time()
        if _out_hdf5 is None or _in_path is None:
            raise TransformExeption("It must be required the output file name.")
            

        with h5py.File(_out_hdf5, 'a') as hf:
            group = hf.create_group(group_name)

            image_list = glob.glob(_in_path)
            for file in image_list:
                if os.path.isfile(file):
                    print("read image : ", file)
                    # read image as binary
                    with open(file, 'rb') as img:
                        bin_image = img.read() # read as binary
                        bin_image_np = np.asarray(bin_image)
                        dset = group.create_dataset(file, data=bin_image_np)
                        print(dset.name, dset.shape, dset.dtype)

        hf.close()
        print("Elapsed Time Performance(sec) : ", time.time()-s_time)

    except TransformExeption as e:
        print("Error : ",e)
    

if __name__ == "__main__":
    #arguments
    parser = argparse.ArgumentParser(description="image2hdf5 -o output_hdf5 -i image_path")
    parser.add_argument('-o', nargs='?', required=True, help="Output HDF5 file")
    parser.add_argument('-i', nargs='?', required=True, help="Input images (path)")
    args = parser.parse_args()

    _out_hdf5 = args.o
    _in_path = args.i+ "*.png"
    
    image2hdfs(_in_path, _out_hdf5)

    