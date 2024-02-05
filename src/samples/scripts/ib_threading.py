# -*- coding: utf-8 -*-
"""
IB API - Daemon Threads

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

import threading
import numpy as np
import time

def randNumGen():
    for a in range(10):
        print(np.random.randint(1,1000))
        time.sleep(1)

thr2 = threading.Thread(target=randNumGen) #creating a separate thread to execute the randNumGen function
thr2.start() #start execution of randNumGen function on the parallel thread

def greeting():
    for i in range(10):
        print("Hello")
        time.sleep(1)
greeting()