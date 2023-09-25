# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

from .Attribute import Attribute

class RgbAttribute(Attribute):

    min = None
    max = None

    def __init__(self):
        self.name = "rgb"
        self.size = 6
        self.numElements = 3
        self.elementSize = 2
        self.type = "uint16"

        self.min = [255, 255, 255]
        self.max = [-255, -255, -255]

    def toObject(self):
        data = super().toObject()
        data['min'] = self.min
        data['max'] = self.max
        return data