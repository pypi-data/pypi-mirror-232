# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

import numpy as np

from ..HNode import HNode
from .PotreeIndexerSampler import PotreeIndexerSampler

class PotreeIndexerSamplerStep(PotreeIndexerSampler):

    step = 3

    def traverse(self, nodes, min: np.ndarray, scale: np.ndarray, spacing: float):
        result = []
        for node in nodes:
            node.sampled = True
            if node.isLeaf():
                continue

            accepted = []
            for childIndex in range(8):
                child = node.children[childIndex]
                if child is None:
                    continue
                if child.numPoints == 0 and child.isLeaf():
                    node.children[childIndex] = None
                    child.buffer = None
                    continue
                if child.numPoints < 500 and child.isLeaf():
                    accepted.extend(child.buffer)
                    node.children[childIndex] = None
                    child.buffer = None
                    continue

                rejected = []
                nums = self._upNodePoints(child.buffer, child.numPoints, accepted, rejected)
                if nums > 0:
                    rejectedNums = len(rejected)
                    child.buffer = rejected
                else:
                    rejectedNums = child.numPoints

                hNode = HNode()
                hNode.name = child.name
                hNode.buffer = child.buffer
                hNode.numPoints = rejectedNums
                hNode.byteOffset = 0
                result.append(hNode)

            if len(accepted) > 0:
                node.numPoints = len(accepted)
                node.buffer.extend(accepted)
            if node.name == "r":
                hNode = HNode()
                hNode.name = node.name
                hNode.buffer = node.buffer
                hNode.numPoints = node.numPoints
                result.append(hNode)

        return result


    def _upNodePoints(self, buffer, numPoints, accepted, rejected):
        nums = 0
        for i in range(numPoints):
            cache = buffer[i]
            if i % self.step == 0:
                nums += 1
                accepted.append(cache)
            else:
                rejected.append(cache)
        return nums

