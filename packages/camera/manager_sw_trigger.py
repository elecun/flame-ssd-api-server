'''
Camera Device Manager for Software Trigger
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
import time
from multiprocessing import Queue


WORKING_PATH = pathlib.Path(__file__).parent
NUM_CAMERAS = 10
TRIGGER_INTERVAL = 0.03 #30ms

g_trigger_on = True
def trigger_work(target, camera_container:pylon.InstantCameraArray):

    try:
        t0 = time.clock_gettime(1)
        print("Target\t" + str(target))
        print("Current time\t" + str(t0))
        print("Delay\t" + str(target - t0))

        for idx, camera in enumerate(camera_container):
            if camera.WaitForFrameTriggerReady(50, pylon.TimeoutHandling_ThrowException):
                camera.ExecuteSoftwareTrigger()
        if g_trigger_on==True:
            threading.Timer(target - t0, trigger_work, [target+TRIGGER_INTERVAL, camera_container]).start()
    except Exception as e:
        print(f"Exception : {e}")

        

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

                camera.TriggerSelector.SetValue('FrameStart')
                camera.AcquisitionMode.SetValue('Continuous')
                camera.TriggerMode.SetValue('On')
                camera.TriggerSource.SetValue('Software')
                camera.TriggerActivation.SetValue('RisingEdge')
                camera.TriggerDelayAbs.SetValue(1.0)

                print("Using device ", camera.GetDeviceInfo().GetFullName())
                

        _camera_container.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_OneByOne)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_UpcomingImage)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_LatestImages)

        # convert pylon image to opencv BGR format
        _converter = pylon.ImageFormatConverter()
        _converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        _converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        # software trigger with thread
        myQueue = Queue()
        target = time.clock_gettime(1)+TRIGGER_INTERVAL
        trigger_work(target, _camera_container)
        
        
        prev_t_tick = timeit.default_timer()
        while _camera_container.IsGrabbing():
            
            # trigger by key
            key = cv2.waitKey(1)
            if key==27:
                g_trigger_on = False
                break

            now_tick = timeit.default_timer()
            grabResult = _camera_container.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            cameraContextValue = grabResult.GetCameraContext()

            #print("Camera ", cameraContextValue, ": ", _camera_container[cameraContextValue].GetDeviceInfo().GetModelName())

            if grabResult.GrabSucceeded():
                image = _converter.Convert(grabResult)
                img = image.GetArray()
                
            fps = float(1/(now_tick-prev_t_tick))
            prev_t_tick = now_tick

            cv2.putText(img, f"fps:{fps})", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2, cv2.LINE_AA)
            cv2.namedWindow(f"{cameraContextValue}", cv2.WINDOW_AUTOSIZE)
            cv2.imshow(f"{cameraContextValue}", img)
            
            grabResult.Release()
        
        _camera_container.StopGrabbing()
        cv2.destroyAllWindows()

    except genicam.GenericException as e:
        print(f"Exception : {e.GetDescription()}")
    except Exception as e:
        print(f"Exception : {e}")
