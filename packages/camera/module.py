'''
Single Camera Module Interface Class
Author : bh.hwang@iae.re.kr
'''

import os
from pypylon import genicam
from pypylon import pylon
import sys
import threading
import signal
import argparse


'''
Single Camera Module Class
'''
class camera_module(threading.Thread):
    def __init__(self, device:pylon.DeviceInfo):
        self.camera = pylon.InstantCamera(tlf.CreateDevice(device))
        #self.camera = pylon.InstantCamera(device.GetDeviceFactory())

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