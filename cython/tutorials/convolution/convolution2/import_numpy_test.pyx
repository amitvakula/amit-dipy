from __future__ import division
import numpy as np
cimport cython

cdef int i;
a = 12

for i in range(10):
	a += i ** 2

cdef int b = 122;
for i in range(12):
	b += i ** 2
