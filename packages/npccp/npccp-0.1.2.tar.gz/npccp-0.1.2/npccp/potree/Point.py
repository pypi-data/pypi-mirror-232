# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

class Point():

    x = None
    y = None
    z = None
    r = None
    g = None
    b = None
    a = None
    index = None

    def __init__(self, x, y, z, a = 0, r = 0, g = 0, b = 0):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_array(self):
        return (self.x, self.y, self.z, self.a, self.b, self.g, self.r, self.index)