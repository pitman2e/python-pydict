import unittest

import pydict.da_jp


class TestSc2Tc(unittest.TestCase):
    def test_sc2tc_part_definition(self):
        txt = "2.（简）简简（簡単な日本語。）"
        results = []
        pydict.da_jp.sc2tc_part_definition(txt, results)

        self.assertEqual(results[0], "2.（簡）簡簡（簡単な日本語。）")