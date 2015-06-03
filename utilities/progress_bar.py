# -*- coding: utf-8 -*-
"""
Created on Sun May 24 14:44:25 2015

@author: support
"""


import pyprind

### PROGRESS BAR EXAMPLE ###
n = 10000000
my_prbar = pyprind.ProgBar(n)   # 1) init. with number of iterations
for i in range(n):
    # do some computation
    my_prbar.update()           # 2) update the progress visualization
    