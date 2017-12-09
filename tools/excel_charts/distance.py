#!/usr/bin/env python3

import math


def deviation(map1, map2, index):
    n = len(map1)
    assert len(map2) == n
    var = 0
    for func, values in map1.items():
        var += (values[index] - map2.get(func, values)[index])**2
    return math.sqrt(var / n)


def pair_changes(map1, map2, index):
    n = len(map1)
    assert len(map2) == n
    p = 0
    keys = list(map1.keys())
    for i in range(n - 1):
        for j in range(i + 1, n):
            d1 = map1[keys[i]][index] - map1[keys[j]][index]
            d2 = map2[keys[i]][index] - map2[keys[j]][index]
            if d1 == 0 and d2 == 0:
                continue
            elif d1 == 0 or d2 == 0:
                p += 1
            elif d1 * d2 < 0:
                p += 1
    return p
