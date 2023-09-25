# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

from .Attribute import Attribute

class PositionAttribute(Attribute):

    min = None
    max = None

    def __init__(self):
        self.name = "position"
        self.size = 12
        self.numElements = 3
        self.elementSize = 4
        self.type = "int32"

        self.min = [None, None, None]
        self.max = [None, None, None]

    def toObject(self):
        data = super().toObject()
        data['min'] = self.min
        data['max'] = self.min
        return data