#!/usr/bin/env python3

import distance
from statistics import mean
from statistics import pstdev
from random import random
import unittest

class TestDistanceMethods(unittest.TestCase):

    def test_deviation(self):
        n = 1000000
        r = [random() for x in range(n)]
        r = [1, 2, 3, 4]
        m = mean(r)
        map1 = {}
        map2 = {}
        for i, v in enumerate(r):
          map1[i] = [v]
          map2[i] = [m]
        self.assertEqual(distance.deviation(map1, map2, 0), pstdev(r, m))

if __name__ == '__main__':
    unittest.main()

