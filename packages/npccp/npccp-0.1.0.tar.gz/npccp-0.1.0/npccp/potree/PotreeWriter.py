# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''
import functools
import json
import os
import struct

import numpy as np

from .HBatch import HBatch
from .HChunk import HChunk
from .Node import Node
from .Point import Point
from .attribute.IndexAttribute import IndexAttribute
from .attribute.IntensityAttribute import IntensityAttribute
from .attribute.PositionAttribute import PositionAttribute
from .attribute.RgbAttribute import RgbAttribute
from .sampler.PotreeIndexerSamplerStep import PotreeIndexerSamplerStep
from .utils.PotreeChunksUtils import doChunking, chunkNodeSort
from .utils.PotreeUtils import getPointDataType, addDescendant, nodeGroup, getHierarchyDataType, \
    getSavePointDataType

class PotreeWriter():

    headerSize = 12
    hierarchyStepSize = 4
    hierarchyNodeSize = 22
    octreePointSize = 24
    octreeOffset = 0

    def __init__(self, pot):
        self._pot = pot
        if os.path.exists(pot):
            os.remove(pot)

        self._numPoints = 0
        self._min = np.zeros(3, dtype=np.float32)
        self._max = np.zeros(3, dtype=np.float32)

        self._positionAttribute = PositionAttribute()
        self._intensityAttribute = IntensityAttribute()
        self._rgbAttribute = RgbAttribute()
        self._indexAttribute = IndexAttribute()

        self._pointDataType = getPointDataType()
        self._savePointDataType = getSavePointDataType()
        self._buffer = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._buffer = np.array(self._buffer, dtype=self._pointDataType)
        self._minmax()
        self._generate()
        return

    def write(self, point: Point):
        point.index = self._numPoints
        self._numPoints += 1
        self._buffer.append(point.to_array())

    def _minmax(self):
        for i, axis in enumerate(['x', 'y', 'z']):
            self._min[i] = min(self._buffer[axis])
            self._max[i] = max(self._buffer[axis])

        self._intensityAttribute.min = int(min(self._buffer['a']))
        self._intensityAttribute.max = int(max(self._buffer['a']))

        for i, color in enumerate(['r', 'g', 'b']):
            self._rgbAttribute.min[i] = int(min(self._buffer[color]))
            self._rgbAttribute.max[i] = int(max(self._buffer[color]))

        self._indexAttribute.max = self._numPoints

    def _generate(self):
        self._positionAttribute.min = self._min.tolist()
        self._positionAttribute.max = self._max.tolist()

        self._min = self._min - 1
        self._max = self._max + 1

        scale = []
        x = str(max(abs(self._min[0]), abs(self._max[0]))).split(".")[0]
        if x == "0":
            scale.append(1e-6)
        else:
            scale.append(pow(10, -6 + len(x)))
        y = str(max(abs(self._min[1]), abs(self._max[1]))).split(".")[0]
        if y == "0":
            scale.append(1e-6)
        else:
            scale.append(pow(10, -6 + len(y)))
        z = str(max(abs(self._min[2]), abs(self._max[2]))).split(".")[0]
        if z == "0":
            scale.append(1e-6)
        else:
            scale.append(pow(10, -6 + len(z)))

        cubeSize = max(self._max - self._min)
        self._max = self._min + cubeSize
        if self._max[0] == 0 or self._max[0] == 0 or self._max[0] == 0:
            raise Exception("坐标点(有无效的点，需要排除)有问题，请处理: " + cubeSize)

        ## 获取有数据的未级节点列表
        chunks = doChunking(self._numPoints, self._max, self._min, self._buffer)
        # 关联节点
        root = Node("r", None, None, None, None)
        for chunkRoot in chunks:
            if len(chunkRoot.name) > 1:
                addDescendant(root, chunkRoot)
        ## 向上级节点分配点
        depth = 0
        sampler = PotreeIndexerSamplerStep()
        data = sampler.sample(root, self._min, scale, 0)
        for node in data:
            depth = max(depth, len(node.name) - 1)
        # ## 分组
        groups = nodeGroup(data, 4)
        #### 生成pot文件
        self._generatePot(groups, depth, scale)

    def _generatePot(self, nodeGroups, depth, scale):

        metadata = self._generateMetadata(depth, scale)
        metadata = json.dumps(metadata).encode("UTF-8")
        metadataSize = len(metadata)
        #######
        batchRoot = self._loadBatch("r", nodeGroups["r"])
        hierarchySize = self.hierarchyNodeSize * len(batchRoot.nodes)

        batches = [self._loadBatch(key, nodeGroups[key]) for key in nodeGroups.keys() if key != "r"]
        for batch in batches:
            self._processBatch(batch)
            hierarchySize += batch.byteSize

        self.octreeOffset = self.headerSize + metadataSize + hierarchySize
        points = []
        hierarchyData = []
        mergeNodes = {}
        bytesWritten = self.headerSize + metadataSize + self.hierarchyNodeSize * len(batchRoot.nodes)

        for batch in batches:
            buffer = self._writeBatchIndexer(batch, bytesWritten, mergeNodes, points)
            hierarchyData.extend(buffer)

            if len(batch.nodes) > 1:
                proxyNode = batchRoot.nodeMap[batch.name]
                proxyNode.type = 2
                proxyNode.childMask = 0
                proxyNode.proxyByteOffset = bytesWritten
                proxyNode.proxyByteSize = self.hierarchyNodeSize * len(batch.chunkMap[batch.name].nodes)
            else:
                rootBatchNode = batchRoot.nodeMap[batch.name]
                rootBatchNode.type = 1
            bytesWritten += len(buffer) * self.hierarchyNodeSize

        rootHierarchyBytes = self._writeBatchIndexer(batchRoot, 0, mergeNodes, points)
        rootHierarchyBytes.extend(hierarchyData)

        with open(self._pot, "wb", buffering=8192) as potRaf:
            potRaf.seek(0)
            potRaf.write(struct.pack("<I", 1)) ## 版本号
            potRaf.write(struct.pack("<I", metadataSize)) ## metadata字节数
            potRaf.write(struct.pack("<I", self.hierarchyNodeSize * len(batchRoot.nodes))) ## 第一个node开始位置
            potRaf.write(metadata) ## metadata内容
            indexData = np.array(rootHierarchyBytes, getHierarchyDataType())
            potRaf.write(indexData.tobytes()) ## hierarchy索引内容

            points = np.array(points, self._pointDataType)
            points['x'] = (points['x'] - self._min[0]) / scale[0]
            points['y'] = (points['y'] - self._min[1]) / scale[1]
            points['z'] = (points['z'] - self._min[2]) / scale[2]
            points = points.astype(getSavePointDataType())
            potRaf.write(points.tobytes()) ## 点数据

    def _generateMetadata(self, depth, scale):
        metadata = {}
        metadata["version"] = "2.2"
        metadata["name"] = "longmao"
        metadata["points"] = self._numPoints

        hierarchy = {}
        hierarchy["stepSize"] = self.hierarchyStepSize
        hierarchy["depth"] = depth
        metadata["hierarchy"] = hierarchy

        metadata["offset"] = self._min.tolist()
        metadata["scale"] = scale
        metadata["spacing"] = 2.1580758906250002

        boundingBox = {}
        boundingBox["min"] = self._min.tolist()
        boundingBox["max"] = self._max.tolist()
        metadata["boundingBox"] = boundingBox

        metadata["encoding"] = "DEFAULT"
        metadata["attributes"] = [
            self._positionAttribute.toObject(),
            self._intensityAttribute.toObject(),
            self._rgbAttribute.toObject(),
            self._indexAttribute.toObject()
        ]
        return metadata

    def _loadBatch(self, name, group):
        batch = HBatch()
        batch.name = name

        for node in group:
            chunkLevel = int((len(node.name) - 2) / 4)
            if node.name == batch.name:
                key = node.name
            else:
                key = node.name[0: self.hierarchyStepSize * chunkLevel + 1]

            if key not in batch.chunkMap:
                chunk = HChunk()
                chunk.name = key
                batch.chunkMap[key] = chunk
                batch.chunks.append(chunk)

            batch.chunkMap[key].nodes.append(node)
            batch.nodes.append(node)
            batch.nodeMap[node.name] = batch.nodes[len(batch.nodes) - 1]

            isChunkKey = (len(node.name) - 1) % self.hierarchyStepSize == 0
            isBatchSubChunk = len(node.name) > self.hierarchyStepSize + 1
            if isChunkKey and isBatchSubChunk:
                if node.name not in batch.chunkMap:
                    chunk = HChunk()
                    chunk.name = node.name
                    batch.chunkMap[node.name] = chunk
                    batch.chunks.append(chunk)
                batch.chunkMap[node.name].nodes.append(node)

        batch.chunks.sort(key = lambda x: len(x.name))
        for node in batch.nodes:
            node.type = 1
            parentName = node.name[0: len(node.name) - 1]
            ptrParent = batch.nodeMap.get(parentName)
            if ptrParent is not None:
                childIndex = int(node.name[len(node.name) - 1])
                ptrParent.type = 0
                ptrParent.childMask = ptrParent.childMask | (1 << childIndex)

        for chunk in batch.chunks:
            ptr = batch.nodeMap.get(chunk.name)
            if ptr is not None:
                ptr.type = 2
            elif chunk.name != batch.name:
                raise Exception("ERROR: could not find chun: " + chunk.name + ", batch:" + batch.name)

        for chunk in batch.chunks:
            chunk.nodes.sort(key = functools.cmp_to_key(chunkNodeSort))

        return batch

    def _processBatch(self, batch:HBatch):
        byteOffset = 0
        for chunk in batch.chunks:
            chunk.byteOffset = byteOffset
            if chunk.name != batch.name:
                parentName = chunk.name[0:len(chunk.name) - self.hierarchyStepSize]
                if batch.chunkMap[parentName] is not None:
                    proxyNode = batch.nodeMap[chunk.name]
                    if proxyNode is None:
                        raise Exception("ERROR: didn't find proxy node")
                    proxyNode.type = 2
                    proxyNode.proxyByteOffset = chunk.byteOffset
                    proxyNode.proxyByteSize = self.hierarchyNodeSize * len(chunk.nodes)
                else:
                    raise Exception("ERROR: didn't find chunk")
            byteOffset += self.hierarchyNodeSize * len(chunk.nodes)
        batch.byteSize = byteOffset

    def _writeBatchIndexer(self, batch: HBatch, offset, mergeNodes, points):
        indexCache = []
        numRecords = 0
        for chunk in batch.chunks:
            numRecords += len(chunk.nodes)
        for chunk in batch.chunks:
            for node in chunk.nodes:
                if node.numPoints > 0 and mergeNodes.get(node.name) is None:
                    mergeNodes[node.name] = True
                    node.byteOffset = self.octreeOffset
                    node.byteSize = node.numPoints * self._savePointDataType.itemsize
                    self.octreeOffset += node.byteSize
                    points.extend(node.buffer)
                    node.buffer = None

                isProxyNode = node.type == 2 and node.name != chunk.name
                type = node.type
                if node.type == 2 and isProxyNode == False:
                    type = 0
                byteSize = node.proxyByteSize if isProxyNode else node.byteSize
                byteOffset = offset + node.proxyByteOffset if isProxyNode else node.byteOffset
                if byteOffset < 0:
                    byteOffset = 0

                indexCache.append((type, node.childMask, node.numPoints, byteOffset, byteSize))
        return indexCache
