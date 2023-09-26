# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''
from .pcd.PcdReader import PcdReader
from .pcd.PcdWriter import PcdWriter

from .potree.Point import Point
from .potree.PotreeWriter import PotreeWriter

def new_potree_point(x, y, z, a = 0, r = 0, g = 0, b = 0):
    return Point(x, y, z, a, r, g, b)

def pcdtopcd(source, target, datatype = 'ascii'):

    with PcdReader(source) as reader:
        header = reader.getHeader()
        header.data = datatype
        with PcdWriter(target, header) as writer:
            while True:
                point = reader.getPoint()
                if point is None:
                    break
                writer.write(point)

def pcdtopot(pcd, pot):

    with PcdReader(pcd) as reader:
        with PotreeWriter(pot) as writer:
            while True:
                point = reader.getPoint()
                if point is None:
                    break

                p = new_potree_point(point['x'], point['y'], point['z'], point['intensity'])
                writer.write(p)