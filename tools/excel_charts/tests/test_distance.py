#!/usr/bin/env python3

import distance
import math
from statistics import mean
from statistics import pstdev
from random import random
import unittest

class TestDistanceMethods(unittest.TestCase):

    def test_deviation(self):
        n = 1000000
        r = [random() for x in range(n)]
        m = mean(r)
        map1 = {}
        map2 = {}
        for i, v in enumerate(r):
          map1[i] = [v]
          map2[i] = [m]
        d1 = distance.deviation(map1, map2, 0)
        d2 = pstdev(r, m)
        self.assertTrue(math.isclose(d1, d2))

    def test_pair_changes(self):
        map1 = {'A': [1], 'B': [2], 'C': [3], 'D': [4], 'E': [5]}
        map2 = {'A': [1], 'B': [3], 'C': [2], 'D': [4], 'E': [5]}
        map3 = {'A': [3], 'B': [2], 'C': [1], 'D': [4], 'E': [5]}
        map4 = {'A': [5], 'B': [1], 'C': [2], 'D': [3], 'E': [4]}
        self.assertEqual(distance.pair_changes(map1, map1, 0), 0)
        self.assertEqual(distance.pair_changes(map1, map2, 0), 1)
        self.assertEqual(distance.pair_changes(map1, map3, 0), 3)
        self.assertEqual(distance.pair_changes(map1, map4, 0), 4)

if __name__ == '__main__':
    unittest.main()

