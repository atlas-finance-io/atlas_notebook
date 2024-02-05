# -*- coding: utf-8 -*-
"""
IB API - Multithreading using events object

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

import threading
import time


def NumGen():
    for a in range(30):
        if event.is_set():
            break
        else:
            print(a)
            time.sleep(1)

event = threading.Event() #creating an event object
thr2 = threading.Thread(target=NumGen) #creating a separate thread to execute the NumGen function
thr2.start() #start execution of NumGen function on the parallel thread

def greeting():
    for i in range(10):
        print("Hello")
        time.sleep(1)
greeting()
event.set() #setting the event flag as true at the completion of the main thread
