# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''
import os
import struct
import numpy as np

try:
    import lzf
except ImportError:
    raise RuntimeError("lzf required. Install with `pip install python-lzf`.")

from .header.PcdHeader import PcdHeader
from .utils.PcdUtils import dataDtype

class PcdWriter():

    def __init__(self, pcd, header: PcdHeader):
        self._pcd = pcd
        self._header = header
        self._points = 0
        self._bufferarray = []

        if os.path.exists(pcd):
            os.remove(pcd)

        self._dtype = dataDtype(header)
        self._writePointMethods = {
            1: self._writeAsciiPoint,
            2: self._writeBinaryPoint,
            3: self._writeBinaryCompressedPoint
        }
        self._writeEndPointMethods = {
            1: self._writeEndAsciiPoint,
            2: self._writeEndBinaryPoint,
            3: self._writeEndBinaryCompressedPoint
        }

    def __enter__(self):
        if self._header.data == "binary":
            self._dataType = 2
        elif self._header.data == "ascii":
            self._dataType = 1
        elif self._header.data == "binary_compressed":
            self._dataType = 3
        else:
            raise Exception('Error data[binary,ascii,binary_compressed] - ' + self._header.data)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._header.points = self._points
        if self._header.width is None:
            self._header.width = self._points

        self._writeEndPointMethods.get(self._dataType, lambda: None)()
        self._bcbuffer = None

    def write(self, point:np.ndarray):
        self._points += 1
        self._writePointMethods.get(self._dataType, lambda: None)(point)

    def _writeAsciiPoint(self, point:np.ndarray):
        self._bufferarray.append(' '.join(map(str, point.astype(self._dtype).tolist())))

    def _writeBinaryPoint(self, point:np.ndarray):
        self._bufferarray.append(point)

    def _writeBinaryCompressedPoint(self, point:np.ndarray):
        self._bufferarray.append(point)

    def _writeEndAsciiPoint(self):
        bos = open(self._pcd, 'w', buffering=8192)
        bos.write(self._header.toString())
        bos.write('\n'.join(self._bufferarray))
        bos.close()

    def _writeEndBinaryPoint(self):
        bos = open(self._pcd, 'wb', buffering=8192)
        bos.write(self._header.toString().encode("UTF-8"))
        bos.write(np.array(self._bufferarray, dtype=self._dtype).tobytes())
        bos.close()

    def _writeEndBinaryCompressedPoint(self):
        uncompressed_data = []
        buffer = np.array(self._bufferarray, self._dtype)
        for name in buffer.dtype.names:
            uncompressed_data.append(buffer[name].tostring())
        uncompressed_data = b''.join(uncompressed_data)
        uncompressed_size = len(uncompressed_data)
        compressed_data = lzf.compress(uncompressed_data)
        compressed_size = len(compressed_data)

        bos = open(self._pcd, 'wb', buffering=8192)
        bos.write(self._header.toString().encode("UTF-8"))
        bos.write(struct.pack('II', compressed_size, uncompressed_size))
        bos.write(compressed_data)
        bos.close()