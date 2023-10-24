'''
Camera Module Interface Class
Author : bh.hwang@iae.re.kr
'''

import os
from pypylon import genicam
from pypylon import pylon
import sys
import threading
import signal

'''
Camera Factory Class
'''
class camera_factory:
    def __init__(self):
        self.tl_factory = pylon.TlFactory.GetInstance() #get instance of pylon transport layer
        self.devices = self.tl_factory.EnumerateDevices()
        print(type(self.tl_factory))

        for device in self.devices:
            print(device.GetModelName(), device.GetSerialNumber())


    # start camera thread independently
    def start(self, camera_list:list):
        pass

    # stop camera thread with 
    def stop(self, camera_list:list):
        pass

    # get camera status
    def get_status(self):
        pass


'''
Single Camera Module Class
'''
class camera_module(threading.Thread):
    def __init__(self, tlf:pylon.TlFactory, device:pylon.DeviceInfo):
        self.camera = pylon.InstantCamera(tlf.CreateDevice(device))

    # open camera device
    def open(self):
        try:
            if not self.camera.IsOpen():
                self.camera.Open()
        except Exception as e:
            print(f"Exception : {e}")

    # threading loop
    def run(self):
        pass


if __name__ == "__main__":
    signal.signal(signal.SIGINT, self.serial_thread_handler)
    _camera_factory = camera_factory()
