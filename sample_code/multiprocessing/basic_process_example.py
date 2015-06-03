# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#import pandas as pd
#path = "/Users/support/example_workbook.xlsx"
#table = pd.read_excel(path, sheetname='Sheet1')

"""
From Python Docs on multiprocessing
"""

from multiprocessing import Process
import os

def info(title):
    print title
    print 'module name:', __name__
    if hasattr(os, 'getppid'):  # only available on Unix
        print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

def f(name):
    info('function f')
    print 'hello', name

if __name__ == '__main__':
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()