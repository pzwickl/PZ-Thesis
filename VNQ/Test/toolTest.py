from app import params, tool
from model import dao, inequality

__author__ = 'patrick'

import unittest
import networkx as nx
#from pattern import Singleton


class LoaderTestCase(unittest.TestCase):

    ut1 = None
    ut2 = None
    g = None

    # PROVIDE THE BASIC GRAPH
    def setUp(self):
        self.ut1 = 5
        self.ut2 = 5

        self.g = nx.MultiDiGraph()
        self.g.add_node(0, name='TestNode1')             # Create node 1
        self.g.add_node(1, name='TestNode2')             # Create node 2
        self.g.add_node(2, name='TestNode3')             # Create node 3
        self.g.add_path([0, 1, 2])                       # Create a path between them (creates several edges = relationships)
        self.g.add_path([2, 1])                          # Second path -> Number of incoming edges: Node 0 = 0; Node 1 = 2; Node 2 = 1

        #ut1 = 5
        test1 = dao.RelationshipInstance('0to1', self.ut1, 0, 0, 0.0)
        test2 = dao.RelationshipInstance('1to2', 10, 0, 0, 0.0)
        test3 = dao.RelationshipInstance('2to1', 1, 0, 0, 0.0)

        helper = tool.Graph.instance()
        helper.safely_add_instances(self.g, 0, 1, 0, test1)   # Add single instance for the first edge between 0 and 1
        helper.safely_add_instances(self.g, 1, 2, 0, test2)   # Add single instance for the first edge between 1 and 2
        helper.safely_add_instances(self.g, 2, 1, 0, test3)   # Add single instance for the first edge between 2 and 1

    def tearDown(self):
        self.g = None
        self.ut1 = None
        self.ut2 = None

    # TEST ENTITY SIZE WITH ONE INSTANCE PER RELATIONSHIP ONLY
    def test_entity_sizes(self):                  # TODO: THROUGH TEST CASE IN JSON
        helper = tool.Graph.instance()
        sizes_in = helper.entity_sizes(self.g, dao.EdgeType.INCOMING)        # nosidepayments.py entity sizes
        ordered_sizes_in = helper.order_results(self.g, sizes_in)            # order them correctly

        fl16 = float(16)

        self.assertAlmostEqual(ordered_sizes_in[0], (0/fl16))             # only pointing away
        self.assertAlmostEqual(ordered_sizes_in[1], (6/fl16))             # 5 + 1 pointing to it
        self.assertAlmostEqual(ordered_sizes_in[2], (10/fl16))            # 10

        sizes_out = helper.entity_sizes(self.g, dao.EdgeType.OUTGOING)     # nosidepayments.py entity sizes
        ordered_sizes_out = helper.order_results(self.g, sizes_out)        # order them correctly

        self.assertAlmostEqual(ordered_sizes_out[0], (self.ut1/fl16))      # 5
        self.assertAlmostEqual(ordered_sizes_out[1], (10/fl16))            # 10
        self.assertAlmostEqual(ordered_sizes_out[2], (1/fl16))             # 1

    # NOW TEST WITH SEVERAL INSTANCES (-> their evaluation should be integrated now)
    # This is a correction factor test
    def test_entity_sizes_2(self):
        helper = tool.Graph.instance()
        #td = TestData(ut1)
        test1_2 = dao.RelationshipInstance('0to1', self.ut2, 0, 0, 0.0)
        helper.safely_add_instances(self.g, 0, 1, 0, test1_2)   # Add second instance between 0 and 1

        node_no = 0
        edge_no = 0

        # The correction factor script has to be run!
        gini = inequality.Gini(self.g, dao.EdgeType.OUTGOING)
        gini.correction_factor(node_no, edge_no, params._WITHIN_RELATIONSHIP_V)                                                     # Sets the correction factor (has to be explicitly called!!

        # Let's find out the new value of the relationship to determine the size
        # Start with the gini for
        gini_result = gini.inequality_within_relationship(node_no, edge_no, params._WITHIN_RELATIONSHIP_V)    # First edge of first node

        #gini_result = inequality.GiniAlgorithm.instance().base_gini([self.ut1, self.ut2], v=3)    # v = 3 for entity size (next block may also be a good unit test itself)

        if self.ut1 > self.ut2:
            best_ut = self.ut1
        else:
            best_ut = self.ut2

        weighted_ut = best_ut * gini_result
        new_sum = 11 + weighted_ut

        sizes_out = helper.entity_sizes(self.g, dao.EdgeType.OUTGOING)               # nosidepayments.py entity sizes
        ordered_sizes_out = helper.order_results(self.g, sizes_out)                  # order them correctly
        #print ordered_sizes_out
        self.assertAlmostEqual(ordered_sizes_out[0], (weighted_ut/float(new_sum)))      # Only the case with two instances should be different now


    def test_JSONTest(self):
        #Test JSON Loader with DAO class
        i = dao.RelationshipInstance('testName', 2.5, 1.0, 1.0, 0.9)
        l = tool.Persistence.instance()

        #fileName = '/test'
        fileName = params._UNIT_TEST_FILE
        l.toJSON(fileName, i)
        iLoaded = l.fromJSON(fileName)

        self.assertEqual(i, iLoaded)

        #Test JSON with graph
        #g = nx.MultiDiGraph()
        #g.add_node(0, name='TestNode1')
        #g.add_node(1, name='TestNode2')
        #g.add_node(2, name='TestNode3')
        #g.add_path([0, 1, 2])
        #g.add_path([2, 1, 0])

        self.g.add_node(14, name='TestNode14')             # Create node 14
        l.toJSON(fileName, self.g)
        actual_g = l.fromJSON(fileName)

        expected_nodes = self.g.nodes()
        actual_nodes = actual_g.nodes()

        for n in range(len(actual_nodes)):
            self.assertTrue(int(actual_nodes[1]) in expected_nodes)     # Type necessary for comparison!

    if __name__ == '__main__':
        suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
        unittest.TextTestRunner(verbosity=2).run(suite)
        #unittest.main()
