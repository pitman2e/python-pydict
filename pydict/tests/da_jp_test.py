import unittest

import pydict.da_jp


class TestSc2Tc(unittest.TestCase):
    def test_sc2tc_to_traditional_1(self):
        txt = "あい体えお"
        results = []
        pydict.da_jp.to_traditional(txt)

        self.assertEqual("あい体えお", pydict.da_jp.to_traditional(txt))


    def test_sc2tc_to_traditional_2(self):
        txt = "あい体えお。体" #LHS: Japanese / RHS: SC
        results = []
        pydict.da_jp.to_traditional(txt)

        self.assertEqual("あい体えお。體", pydict.da_jp.to_traditional(txt))


    def test_sc2tc_part_definition_1(self):
        txt = "2.（体）体体（体力日本語。）"
        results = []
        pydict.da_jp.sc2tc_part_definition(txt, results)

        self.assertEqual("2.（體）體體（体力日本語。）", results[0])


    def test_sc2tc_part_definition_2(self):
        # 当てつけ
        txt = "あい体えお"
        results = []
        pydict.da_jp.sc2tc_part_definition(txt, results)

        self.assertEqual("あい体えお", results[0])


    def test_sc2tc_part_definition_3(self):
        # 当てつけ
        txt = "体体, 体体"
        results = []
        pydict.da_jp.sc2tc_part_definition(txt, results)

        self.assertEqual(results[0], "體體, 體體")

