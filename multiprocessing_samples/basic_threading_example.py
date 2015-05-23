# -*- coding: utf-8 -*-
"""
Created on Fri May 22 11:02:53 2015

@author: support
"""

"""
Code from http://pymotw.com/2/threading/
"""
import threading

def worker():
    """thread worker function"""
    print 'Worker ' +  str(threading.currentThread().ident)
    return

threads = []
for i in range(5):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()