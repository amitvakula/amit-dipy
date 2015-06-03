# -*- coding: utf-8 -*-
"""
Created on Thu May 28 11:44:30 2015

@author: support
"""

import multiprocessing


def func():
    def sub_function(a):
        return a + 1    
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    results = p.map(sub_function, list(i for i in range(100)))
    return results


# expecting Pickling error because using a sub-function
try:
    test_one_results = func()
catch: