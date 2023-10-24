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
import datetime
import cv2
import timeit

from image_event_printer import ImageEventPrinter
from configuration_event_printer import ConfigurationEventPrinter

WORKING_PATH = pathlib.Path(__file__).parent
NUM_CAMERAS = 10

'''
Manager Entry
'''
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', nargs='?', required=False, help="Configuration file")
    args = parser.parse_args()

    try:
        _config_path = None
        if args.config is not None:
            config_path = WORKING_PATH / pathlib.Path(args.config)

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
                

        _camera_container.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_OneByOne)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_UpcomingImage)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_LatestImages)

        # convert pylon image to opencv BGR format
        _converter = pylon.ImageFormatConverter()
        _converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        _converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        # grab
        
        while _camera_container.IsGrabbing():
            start = timeit.default_timer()

            grabResult = _camera_container.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            cameraContextValue = grabResult.GetCameraContext()
            #print("Camera ", cameraContextValue, ": ", _camera_container[cameraContextValue].GetDeviceInfo().GetModelName())

            if grabResult.GrabSucceeded():
                image = _converter.Convert(grabResult)
                img = image.GetArray()
                end = timeit.default_timer()
                fps = float(1/(end-start))
                cv2.putText(img, f"fps:{fps})", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2, cv2.LINE_AA)
                cv2.namedWindow(f"{cameraContextValue}", cv2.WINDOW_NORMAL)
                cv2.imshow(f"{cameraContextValue}", img)
                k = cv2.waitKey(1)
                if k == 27:
                    break
            
            grabResult.Release()
            
        _camera_container.StopGrabbing()
        cv2.destroyAllWindows()

    except genicam.GenericException as e:
        print(f"Exception : {e.GetDescription()}")
    except Exception as e:
        print(f"Exception : {e}")
