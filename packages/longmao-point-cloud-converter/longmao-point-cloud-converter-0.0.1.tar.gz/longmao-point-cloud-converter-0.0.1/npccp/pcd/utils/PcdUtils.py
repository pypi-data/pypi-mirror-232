# coding=utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023-09-20
@author: nayuan
'''
import numpy as np

from npccp.pcd.header.PcdHeader import PcdHeader

def dataDtype(header: PcdHeader):
    numpy_pcd_type_mappings = [(np.dtype('float32'), ('F', 4)),
                               (np.dtype('float64'), ('F', 8)),
                               (np.dtype('uint8'), ('U', 1)),
                               (np.dtype('uint16'), ('U', 2)),
                               (np.dtype('uint32'), ('U', 4)),
                               (np.dtype('uint64'), ('U', 8)),
                               (np.dtype('int16'), ('I', 2)),
                               (np.dtype('int32'), ('I', 4)),
                               (np.dtype('int64'), ('I', 8))]
    pcd_type_to_numpy_type = dict((q, p) for (p, q) in numpy_pcd_type_mappings)

    names = []
    types = []
    for f, c, t, s in zip(header.fields, header.count, header.type, header.size):
        type = pcd_type_to_numpy_type[(t, s)]
        if c == 1:
            names.append(f)
            types.append(type)
        else:
            names.extend(['%s_%04d' % (f, i) for i in range(c)])
            types.extend([type] * c)
    return np.dtype(list(zip(names, types)))