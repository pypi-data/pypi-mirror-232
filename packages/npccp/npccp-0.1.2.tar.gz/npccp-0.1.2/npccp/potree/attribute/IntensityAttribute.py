# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

from .Attribute import Attribute

class IntensityAttribute(Attribute):

    min = None
    max = None

    def __init__(self):
        self.name = "intensity"
        self.size = 2
        self.numElements = 1
        self.elementSize = 2
        self.type = "uint16"

        self.min = 255
        self.max = -255


    def toObject(self):
        data = super().toObject()
        data['min'] = [self.min]
        data['max'] = [self.max]
        return data