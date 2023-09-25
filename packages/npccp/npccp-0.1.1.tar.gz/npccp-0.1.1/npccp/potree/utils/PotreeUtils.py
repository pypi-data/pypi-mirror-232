# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

import numpy as np

from ..Node import Node

def getHierarchyDataType():
    names = ['type', 'childMask', 'numPoints', 'byteOffset', 'byteSize']
    types = [np.dtype('uint8'), np.dtype('uint8'), np.dtype('uint32'), np.dtype('uint64'), np.dtype('uint64')]
    return np.dtype(list(zip(names, types)))

def getXyzDataType():
    names = ['x', 'y', 'z']
    types = [np.dtype('float32'), np.dtype('float32'), np.dtype('float32')]
    return np.dtype(list(zip(names, types)))

def getPointDataType():
    names = ['x', 'y', 'z', 'r', 'g', 'b', 'a', 'index']
    types = [np.dtype('float32'), np.dtype('float32'), np.dtype('float32'), np.dtype('int16'), np.dtype('int16'), np.dtype('int16'), np.dtype('int16'), np.dtype('uint32')]
    return np.dtype(list(zip(names, types)))

def getSavePointDataType():
    names = ['x', 'y', 'z', 'r', 'g', 'b', 'a', 'index']
    types = [np.dtype('int32'), np.dtype('int32'), np.dtype('int32'), np.dtype('int16'), np.dtype('int16'), np.dtype('int16'), np.dtype('int16'), np.dtype('uint32')]
    return np.dtype(list(zip(names, types)))

def addDescendant(current: Node, descendant: Node):
    descendantLevel = len(descendant.name) - 1
    for level in range(1, descendantLevel):
        index = int(descendant.name[level])
        if current.children[index] is not None:
            current = current.children[index]
        else:
            childName = current.name + str(index)
            child = Node(childName, None, None, 0)
            current.children[index] = child
            current = child

    index = int(descendant.name[descendantLevel])
    current.children[index] = descendant

def nodeGroup(nodes, hierarchyStepSize):
    groups = {}
    for node in nodes:
        if len(node.name) <= hierarchyStepSize + 1:
            key = "r"
        else:
            key = node.name[0: hierarchyStepSize + 1]

        if key not in groups:
            groups[key] = []
        groups[key].append(node)

        if len(node.name) == hierarchyStepSize + 1:
            if node.name not in groups:
                groups[node.name] = []
            groups[node.name].append(node)
    return groups