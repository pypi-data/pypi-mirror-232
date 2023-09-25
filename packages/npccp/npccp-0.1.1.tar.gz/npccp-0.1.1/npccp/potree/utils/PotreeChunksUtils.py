# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

import numpy as np

from collections import deque
from ..Node import Node

__pointIndexScale = 1000
__maxNodePoints = 10000

def doChunking(numPoints, _max:np.ndarray, _min:np.ndarray, buffer:np.ndarray):
    if numPoints < 100_0000:
        maxLevel = 10
    elif numPoints < 1000_0000:
        maxLevel = 20
    else:
        maxLevel = 30

    q = deque()
    q.append(Node("r", max(_max - _min), _min, numPoints, buffer))

    chunks = []
    while len(q) > 0:
        root = q.popleft()
        childs = _buildChildes(root, chunks)
        for child in childs:
            if child is None or child.numPoints == 0:
                continue
            if len(child.name) < maxLevel and child.numPoints >= __maxNodePoints:
                q.append(child)
            else:
                chunks.append(child)

    return chunks

def _buildChildes(root:Node, chunks):
    childes = [None] * 8
    size = int(root.size * __pointIndexScale / 2)
    if size < 100:
        chunks.append(root)
        return childes

    for point in root.buffer:
        x = int(abs(point[0] - root.min[0]) * __pointIndexScale)
        y = int(abs(point[1] - root.min[1]) * __pointIndexScale)
        z = int(abs(point[2] - root.min[2]) * __pointIndexScale)

        nx = min(1, int(x / size)) << 2
        ny = min(1, int(y / size)) << 1
        nz = min(1, int(z / size))
        index = nx + ny + nz

        if childes[index] is None:
            nx = 1 if nx > 0 else 0
            ny = 1 if ny > 0 else 0
            nz = 1 if nz > 0 else 0
            minX = root.min[0] + nx * root.size / 2
            minY = root.min[1] + ny * root.size / 2
            minZ = root.min[2] + nz * root.size / 2
            childes[index] = Node(root.name + str(index), root.size / 2, (minX, minY, minZ), 0)
        childes[index].addNumPoints(1)
        childes[index].write(point)
    root.buffer = None
    return childes

def chunkNodeSort(a, b):
    if len(a.name) != len(b.name):
        return -1 if len(a.name) < len(b.name) else 1
    elif a.name == b.name:
        return 0
    elif a.name > b.name:
        return 1
    else:
        return -1
