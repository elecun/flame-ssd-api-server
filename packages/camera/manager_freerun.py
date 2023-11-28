'''
Camera Device Manager
Author : bh.hwang@iae.re.kr
'''

import os
from pypylon import genicam
from pypylon import pylon
import sys
import threading
import signal
import argparse
import pathlib
from module import camera_module
import cv2
from datetime import datetime
import signal
from joblib import Parallel, delayed, parallel_backend
import redis
import numpy as np
import h5py


WORKING_PATH = pathlib.Path(__file__).parent
NUM_CAMERAS = 10

#(Note) acA1300-60gc = 125MHz(PTP disabled), 1 Tick = 8ns
#(Note) a2A1920-51gmPRO = 1GHZ, 1 Tick = 1ns
CAMERA_TICK_TIME = 8 

'''
Manager Entry
'''
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--use_camera', nargs='?', default=False, required=False, help="use camera for testing")
    parser.add_argument('--use_image', nargs='?', default=False, required=True, help="use image for testing")
    parser.add_argument('--config', nargs='?', required=False, type=str, help="Configuration file")
    parser.add_argument('--show', nargs='?', default="true", required=False, help="Display Image on Window")
    parser.add_argument('--test_file_saving', nargs='?', default=False, required=False, help="Testing for saving image file from memory data")
    parser.add_argument('--test_redis_saving', nargs='?', default=False, required=False, help="Testing for saving to redis from memory data")
    parser.add_argument('--test_convert_hdf5_from_memory', nargs='?', default=False, required=False, help="Testing for Converting images to HDF5")
    args = parser.parse_args()

    try:
        _config_path = None
        _show = True
        if args.config is not None:
            _config_path = WORKING_PATH / pathlib.Path(args.config)
        if args.show is not None:
            if str(args.show).lower() in ('true', 't', 'y', 'yes'):
                _show = True
            elif str(args.show).lower() in ('false', 'f', 'n', 'no'):
                _show = False
            else:
                raise argparse.ArgumentTypeError("--show option requires true or false")

        _store_path = WORKING_PATH / "capture"
        _store_path.mkdir(parents=True, exist_ok=True)
        
        # get connected cameras
        if args.use_camera:
            _tlf = pylon.TlFactory.GetInstance()
            _devices = _tlf.EnumerateDevices()
            print(f"Found {len(_devices)} Camera(s)")
            if len(_devices)==0:
                raise pylon.RuntimeException("No cameras present")
            
            # setup camera array
            _camera_container = pylon.InstantCameraArray(len(_devices))
            
            for idx, camera in enumerate(_camera_container):
                if not camera.IsPylonDeviceAttached():
                    camera.Attach(_tlf.CreateDevice(_devices[idx]))
                    camera.Open()

                    print("Using device ", camera.GetDeviceInfo().GetFullName())
                    
            # select one
            _camera_container.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByUser)
            #_camera_container.StartGrabbing(pylon.GrabStrategy_OneByOne, pylon.GrabLoop_ProvidedByUser)
            #_camera_container.StartGrabbing(pylon.GrabStrategy_UpcomingImage, pylon.GrabLoop_ProvidedByUser)
            #_camera_container.StartGrabbing(pylon.GrabStrategy_LatestImages)

            # convert pylon image to opencv BGR format
            _converter = pylon.ImageFormatConverter()
            _converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            _converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            # grab
            _grab_result = {}
            _grab_tick = {}
            _test_count = 0
            
            _t_total_start = datetime.now()
            _store_buffer = {}
            for i in len(_devices):
                _store_buffer[i] = []

            while _camera_container.IsGrabbing():
                print(f"Test Count :{_test_count}")
                if _test_count==(30*13): # 13 sec x 30fps 
                    print("Test Done")
                    break

                for cam_idx, camera in enumerate(_camera_container):
                    _grab_result[cam_idx] = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                    _fps = 0

                    if _grab_result[cam_idx].GrabSucceeded():
                        image = _converter.Convert(_grab_result[cam_idx])
                        raw_image = image.GetArray()

                        # for test (file saving)
                        #cv2.imwrite(str(_store_path/f"{cam_idx}_{_test_count}.png"), raw_image)

                        # for test (memory buffer)
                        _store_buffer[cam_idx].append(raw_image)

                    if _show==True:
                        _now_tick = _grab_result[cam_idx].GetTimeStamp()
                        if len(_grab_tick)==_camera_container.GetSize():
                            _fps = 1/((_now_tick - _grab_tick[cam_idx])*CAMERA_TICK_TIME/1000000000)
                            cv2.putText(raw_image, f"fps:{_fps:.1f}", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2, cv2.LINE_AA)
                        _grab_tick[idx] = _now_tick
                    
                        cv2.namedWindow(f"{cam_idx}", cv2.WINDOW_AUTOSIZE)
                        cv2.imshow(f"{cam_idx}", raw_image)

                    _grab_result[cam_idx].Release()
                
                _test_count+=1 # increate count
                
                key = cv2.waitKey(1)
                if key == 27: # ESC
                    break

        if args.use_image:
            print("Start to load a image...")
            _t_start = datetime.now()
            n_sample = 40*15
            camera = 10

            _store_buffer = {}
            for i in range(camera):
                _store_buffer[i] = []
            
            for cam_idx in range(camera):
                for idx in range(n_sample):
                    raw_image = cv2.imread("./test_image/sample.png")
                    _store_buffer[cam_idx].append(raw_image)
                print(f"ready to load for camera {cam_idx}")

            _t_end = datetime.now()
            print(f"Elapsed Time (Load image on memory) : {(_t_end-_t_start).total_seconds()}")


        _t_total_start = datetime.now()

        # save image to file from memory buffer
        def test_saving_file(cam_idx):
            for idx, image in enumerate(_store_buffer[cam_idx]):
                print(f"saving {cam_idx}-{idx}")
                cv2.imwrite(str(_store_path/f"{cam_idx}_{idx}.png"), image)


        # save image to file from memory buffer with Parallelism
        if args.test_file_saving:
            _t_start_test_file_saving = datetime.now()
            Parallel(n_jobs=16, prefer="threads")(delayed(test_saving_file)(k) for k in _store_buffer)
            _t_end_test_file_saving = datetime.now()
            print(f"Elapsed Time (saving into file) : {(_t_end_test_file_saving-_t_start_test_file_saving).total_seconds()}")

        if args.test_redis_saving:
            _t_start_test_redis_saving = datetime.now()
            try:
                redis_handle = redis.StrictRedis(host='localhost', port=6379)
                #for cam_idx, camera_buffer in enumerate(_store_buffer):
                for cam_idx in range(10):
                    for idx, image in enumerate(_store_buffer[cam_idx]):
                        img_bytes = np.array2string(image)
                        redis_handle.set(f"camera{cam_idx}_{idx}",img_bytes)
                    print(f"stored into redis {cam_idx}")

                redis_handle.close()
            except Exception as e:
                print(e)
            
            _t_end_test_redis_saving = datetime.now()
            print(f"Elapsed Time (storing into redis) : {(_t_end_test_redis_saving-_t_start_test_redis_saving).total_seconds()}")

        elif args.test_convert_hdf5_from_memory:
            try:
                with h5py.File("hdf5_full", 'a') as hf:
                    group = hf.create_group("dataset")
                    #for cam_idx, camera_buffer in enumerate(_store_buffer):
                    for cam_idx in range(10):
                        for idx, image in enumerate(_store_buffer[cam_idx]):
                            image_np = np.asarray(image)
                            dset = group.create_dataset(f"camera{cam_idx}_{idx}", data=image_np)
                hf.close()

            except Exception as e:
                print(e)

        _t_total_end = datetime.now()
        print(f"Elapsed Time : {(_t_total_end-_t_total_start).total_seconds()}")

        if args.use_camera:    
            _camera_container.StopGrabbing()
            _camera_container.Close()

        cv2.destroyAllWindows()

    except genicam.GenericException as e:
        print(f"Exception : {e}")
    except Exception as e:
        print(f"Exception : {e}")
    except KeyboardInterrupt as e:
        if _camera_container.IsGrabbing():
            _camera_container.StopGrabbing()
            _camera_container.Close()
        print(f"Program Terminated")
