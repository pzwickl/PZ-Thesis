from model import inequality

__author__ = 'patrick'

import unittest


class MyTestCase(unittest.TestCase):
    def test_baseGini(self):
        #g = nx.MultiDiGraph()
        #ineq = inequality.Gini(g, dao.EdgeType.INCOMING)
        utilities = [1]
        ga = inequality.GiniAlgorithm.instance()
        self.assertEqual(ga.base_gini(utilities, 2), 1)
        self.assertEqual(ga.base_gini(utilities, 3), 1)

        utilities = [1, 0.9, 0.8]
        self.assertAlmostEqual(ga.base_gini(utilities, 3), 0.1138545953)
        self.assertAlmostEqual(ga.base_gini(utilities, 2), 0.3360768176)

    # More tests on Gini class itself asre also in the toolTest (due to overlap)

if __name__ == '__main__':
    unittest.main()
