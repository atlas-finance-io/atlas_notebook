# -*- coding: utf-8 -*-
"""
IB API - Daemon Threads

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

import threading
import time

def NumGen():
    for a in range(30):
        print(a)
        time.sleep(1)

thr2 = threading.Thread(target=NumGen) #creating a separate thread to execute the NumGen function
thr2.daemon=True #defining the thread as daemon
thr2.start() #start execution of NumGen function on the parallel thread

def greeting():
    for i in range(10):
        print("Hello")
        time.sleep(1)
greeting()