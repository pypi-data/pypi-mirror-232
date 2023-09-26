# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

class Node():

    size = 0
    min = None
    name:str = None
    numPoints = 0
    children = None
    buffer = None

    sampled = False
    __bos = None

    def __init__(self, name, size, min, numPoints, buffer=None):
        if buffer is None:
            buffer = []
        self.name = name
        self.size = size
        self.min = min
        self.numPoints = numPoints
        self.buffer = buffer
        self.children = [None]*8

    def addNumPoints(self, num):
        self.numPoints += num

    def isLeaf(self):
        for child in self.children:
            if child is not None: return False
        return True

    def write(self, point):
        self.buffer.append(point)