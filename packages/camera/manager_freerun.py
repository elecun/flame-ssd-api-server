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
import timeit
import signal


WORKING_PATH = pathlib.Path(__file__).parent
NUM_CAMERAS = 10

'''
Manager Entry
'''
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', nargs='?', required=False, type=str, help="Configuration file")
    parser.add_argument('--show', nargs='?', default="true", required=False, help="Display Image on Window")
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

        # get connected cameras
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
                

        #_camera_container.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        _camera_container.StartGrabbing(pylon.GrabStrategy_OneByOne, pylon.GrabLoop_ProvidedByUser)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_UpcomingImage)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_LatestImages)

        # convert pylon image to opencv BGR format
        _converter = pylon.ImageFormatConverter()
        _converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        _converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        # grab
        _grab_result = {}
        while _camera_container.IsGrabbing():
            start = timeit.default_timer()

            for idx, camera in enumerate(_camera_container):
                _grab_result[idx] = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

                if _grab_result[idx].GrabSucceeded():
                    image = _converter.Convert(_grab_result[idx])
                    raw_image = image.GetArray()
                
                if _show==True:
                    cv2.namedWindow(f"{idx}", cv2.WINDOW_AUTOSIZE)
                    cv2.imshow(f"{idx}", raw_image)

                _grab_result[idx].Release()
            
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break
            
        _camera_container.StopGrabbing()
        cv2.destroyAllWindows()

    except genicam.GenericException as e:
        print(f"Exception : {e.GetDescription()}")
    except Exception as e:
        print(f"Exception : {e}")
    except KeyboardInterrupt as e:
        if _camera_container.IsGrabbing():
            _camera_container.StopGrabbing()
        print(f"Program Terminated")
