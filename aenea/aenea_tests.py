#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Aenea - Tests
"""
import unittest
from aenea import *

class TestAenea(unittest.TestCase):
    """
    Our basic test class
    """

    def test_fact(self):
        """
        The actual test.
        Any method which starts with ``test_`` will considered as a test case.
        This is a build test in fact.
        """
        res = ayuda("testbot",5)
        self.assertEqual(res, 120)


if __name__ == '__main__':
    unittest.main()