import unittest

import pydict.da_jp


class TestSc2Tc(unittest.TestCase):
    def test_sc2tc_to_traditional_1(self):
        txt = "あい简えお"
        results = []
        pydict.da_jp.to_traditional(txt)

        self.assertEqual(pydict.da_jp.to_traditional(txt), "あい简えお")


    def test_sc2tc_to_traditional_2(self):
        txt = "あい简えお。简简简" #LHS: Japanese / RHS: SC
        results = []
        pydict.da_jp.to_traditional(txt)

        self.assertEqual(pydict.da_jp.to_traditional(txt), "あい简えお。簡簡簡")


    def test_sc2tc_part_definition_1(self):
        txt = "2.（简）简简（簡単な日本語。）"
        results = []
        pydict.da_jp.sc2tc_part_definition(txt, results)

        self.assertEqual(results[0], "2.（簡）簡簡（簡単な日本語。）")