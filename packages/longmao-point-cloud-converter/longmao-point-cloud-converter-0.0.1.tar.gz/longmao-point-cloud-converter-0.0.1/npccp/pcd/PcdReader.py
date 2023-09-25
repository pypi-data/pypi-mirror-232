# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''

import numpy as np
import re
import struct
import lzf

from npccp.pcd.utils.PcdUtils import dataDtype
from npccp.pcd.header.PcdHeader import PcdHeader

class PcdReader():

    def __init__(self, pcd):
        self._pcd = pcd
        self._bis = open(self._pcd, "rb", buffering=8192)
        self._header = self._loadHeader()
        self._checkData()

        self._get_point_methods = {
            1: self._getAsciiPoint,
            2: self._getBinaryPoint,
            3: self._getBinaryCompressedPoint
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._bis is not None:
            self._bis.close()
            self._bcbuffer = None

    def getHeader(self):
        return self._header

    def getPoint(self):
        return self._get_point_methods.get(self._dataType, lambda: None)()

    def _getAsciiPoint(self):
        return self._getBinaryCompressedPoint()

    def _getBinaryPoint(self):
        self._offset += 1
        if self._end:
            return None
        elif self._offset >= self._bufferSize:
            cache = self._bis.read(10000 * self._dtype.itemsize)
            if len(cache) == 0:
                self._end = True
                return None
            self._buffer = np.frombuffer(cache, dtype=self._dtype)
            self._bufferSize = len(self._buffer)
            self._offset = 0
        return self._buffer[self._offset]

    def _getBinaryCompressedPoint(self):
        self._offset += 1
        if self._offset >= self._points:
            return None
        return self._buffer[self._offset]

    def _checkData(self):

        if self._header.count is None:
            self._header.count = np.ones(len(self._header.fields))

        self._offset = -1
        self._dtype = dataDtype(self._header)

        if self._header.data == "binary":
            self._dataType = 2
            self._end = False
            self._bufferSize = 0
        elif self._header.data == "ascii":
            self._dataType = 1
            self._points = self._header.points
            self._buffer = np.loadtxt(self._bis, dtype=self._dtype, delimiter=' ')
        elif self._header.data == "binary_compressed":
            self._dataType = 3
            compressed_size, uncompressed_size = struct.unpack('II', self._bis.read(struct.calcsize('II')))
            compressed_data = self._bis.read(compressed_size)
            uncompressed_data = lzf.decompress(compressed_data, uncompressed_size)
            if len(uncompressed_data) != uncompressed_size: raise Exception('Error decompressing data')

            data = np.zeros(self._header.width, self._dtype)
            ix = 0
            for dti in range(len(self._dtype)):
                dt = self._dtype[dti]
                bytes = dt.itemsize * self._header.width
                column = np.fromstring(uncompressed_data[ix:(ix+bytes)], dt)
                data[self._dtype.names[dti]] = column
                ix += bytes

            self._points = len(data)
            self._buffer = data

            self._bis.close()
            self._bis = None
        else:
            raise Exception("不支持的数据类型(DATA):" + self._header.data)

    def _loadHeader(self):
        header = PcdHeader()
        type_converters = {
            "version": str,
            "width": int,
            "height": int,
            "points": int,
            "fields": lambda x: np.array(re.split(r"\s+", x)),
            "type": lambda x: np.array(re.split(r"\s+", x)),
            "size": lambda x: np.array(re.split(r"\s+", x), dtype=np.int8),
            "count": lambda x: np.array(re.split(r"\s+", x), dtype=np.int8),
            "viewpoint": lambda x: np.array(re.split(r"\s+", x), dtype=np.float32)
        }

        while True:
            line = self._bis.readline().strip()
            if line == "":
                break
            kv = re.split(r"\s+", line.decode('utf-8'), 1)
            name = kv[0].lower()

            if name in type_converters:
                setattr(header, name, type_converters[name](kv[1]))
            elif name == "data":
                setattr(header, name, kv[1].lower())
                break
        return header