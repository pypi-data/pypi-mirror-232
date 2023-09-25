# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

class HBatch():

    name = None
    byteSize = 0

    nodes = None
    nodeMap = None

    chunks = None
    chunkMap = None

    def __init__(self):
        self.nodes = []
        self.nodeMap = {}
        self.chunks = []
        self.chunkMap = {}