# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

from .PcdHeader import PcdHeader

class PcdXyziHeader(PcdHeader):

    fields = ["x","y","z","intensity"]
    size = [4,4,4,4]
    type = ["F","F","F","F"]
    count = [1,1,1,1]