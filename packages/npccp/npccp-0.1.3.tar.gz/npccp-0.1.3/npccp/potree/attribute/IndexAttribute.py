# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

from .Attribute import Attribute

class IndexAttribute(Attribute):

    min = None
    max = None

    def __init__(self):
        self.name = "index"
        self.size = 4
        self.numElements = 1
        self.elementSize = 4
        self.type = "uint32"

        self.min = 0
        self.max = 0

    def toObject(self):
        data = super().toObject()
        data['min'] = [self.min]
        data['max'] = [self.max]
        return data