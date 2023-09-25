# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-13
@author: nayuan
'''
import struct

def bytesValue(bytes, size, type):
    match type:
        case "F":
            if size == 4:
                return struct.unpack('f', bytes)[0]
            else:
                return struct.unpack('d', bytes)[0]
        case "U":
            if size == 8:
                return struct.unpack('I', bytes)[0]
            else:
                return struct.unpack('H', bytes)[0]
        case "I":
            if size == 8:
                return struct.unpack('i', bytes)[0]
            else:
                return struct.unpack('h', bytes)[0]
        case "S":
            return struct.unpack('S', bytes)[0]
    return None