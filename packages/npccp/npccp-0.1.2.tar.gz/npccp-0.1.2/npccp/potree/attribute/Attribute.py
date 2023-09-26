# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

class Attribute():

    name = None
    size = None
    numElements = None
    elementSize = None
    type = None

    def toObject(self):
        data = {}
        data['name'] = self.name
        data['size'] = self.size
        data['numElements'] = self.numElements
        data['elementSize'] = self.elementSize
        data['type'] = self.type
        return data