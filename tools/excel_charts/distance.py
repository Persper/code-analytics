#!/usr/bin/env python3

import math

def deviation(map1, map2, index):
    n = len(map1)
    assert len(map2) == n
    var = 0
    for func, values in map1.items():
        var += (values[index] - map2.get(func, values)[index])**2
    return math.sqrt(var / n)

