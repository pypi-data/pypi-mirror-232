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

class PotreeIndexerSampler():

    def sample(self, root: Node, min: np.ndarray, scale: np.ndarray, spacing:float):
        nodes = []
        ## 获取所有node
        q = deque()
        q.append(root)
        while len(q) > 0:
            node = q.popleft()
            nodes.append(node)
            for child in node.children:
                if child is None:
                    continue
                q.append(child)
        nodes.reverse()
        return self.traverse(nodes, min, scale, spacing)

    def traverse(self, nodes: [Node], min: np.ndarray, scale: np.ndarray, spacing: float):
        return
