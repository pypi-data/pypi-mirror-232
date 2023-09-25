# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

class PcdHeader():

    DATA_TYPE_ASCII = 'ascii'
    DATA_TYPE_BINARY = 'binary'
    DATA_TYPE_BINARY_COMPRESSED = 'binary_compressed'

    version = "0.7"
    fields = None
    size = None
    type = None
    count = None
    width = None
    height = 1
    viewpoint = [0.0,0.0,0.0,1.0,0.0,0.0,0.0],
    points = 0
    data = "ascii"

    def toString(self):
        template = """# .PCD v{version} - Point Cloud Data file format - longmao
VERSION {version}
FIELDS {fields}
SIZE {size}
TYPE {type}
COUNT {count}
WIDTH {width}
HEIGHT {height}
VIEWPOINT {viewpoint}
POINTS {points}
DATA {data}
"""
        str_replace = {}
        str_replace['version'] = str(self.version)
        str_replace['fields'] = ' '.join(self.fields)
        str_replace['size'] = ' '.join(map(str, self.size))
        str_replace['type'] = ' '.join(self.type)
        str_replace['count'] = ' '.join(map(str, self.count))
        str_replace['width'] = str(self.width)
        str_replace['height'] = str(self.height)
        str_replace['viewpoint'] = ' '.join(map(str, self.viewpoint))
        str_replace['points'] = str(self.points)
        str_replace['data'] = self.data

        return template.format(**str_replace)
