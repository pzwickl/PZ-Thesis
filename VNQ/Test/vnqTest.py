from app import params, tool
from controller import vnqcontroller
from model import dao

__author__ = 'patrick'

import unittest
import networkx as nx


class VNQTestCase(unittest.TestCase):

    def integrate_entity_size(self, size):
        return (1 - size)

    def setUp(self):
        self.ut1 = 5
        self.ut2 = 5
        self.entity_sizes = [0, 0, 0, 0, 0, 0, 0, 0]    # Test without entity sizes ... if with automatic computation set to []


        # "Unbalanced" Graph
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

        # "Balanced" graph
        self.g2 = nx.MultiDiGraph()
        self.g2.add_node(0, name='TestNode1')             # Create node 1
        self.g2.add_node(1, name='TestNode2')             # Create node 2
        self.g2.add_node(2, name='TestNode3')             # Create node 3
        self.g2.add_path([0, 1, 2])                       # Create a path between them (creates several edges = relationships)
        self.g2.add_path([2, 0])                          # Second path -> Number of incoming edges: Node 0 = 0; Node 1 = 2; Node 2 = 1

        #ut1 = 5
        test1 = dao.RelationshipInstance('0to1', self.ut1, 0, 0, 0.0)
        test2 = dao.RelationshipInstance('1to2', 10, 0, 0, 0.0)
        test3 = dao.RelationshipInstance('2to0', 1, 0, 0, 0.0)

        helper = tool.Graph.instance()
        helper.safely_add_instances(self.g2, 0, 1, 0, test1)   # Add single instance for the first edge between 0 and 1
        helper.safely_add_instances(self.g2, 1, 2, 0, test2)   # Add single instance for the first edge between 1 and 2
        helper.safely_add_instances(self.g2, 2, 0, 0, test3)   # Add single instance for the first edge between 2 and 1


    def tearDown(self):
        self.g = None
        self.ut1 = None
        self.ut2 = None

    def test_dependencyIndicatorBargainingPower_automatic_entity_size(self):
        vn = vnqcontroller.VNQController()
        power = [0.5, 1]
        #size = self.entity_sizes
        size = [1, 0.5]
        #W1 = [params._W1, params_W1]

        #This reproduces the logic in short with generated data

        #for p,s in zip(power,size):

        opp_entity_sizes = [self.integrate_entity_size(e) for e in size]               # 1 - entity_size for direct integration in the next step

        # Manual nosidepayments.py the weighted bargaining power factor
        intermediary_result = [a*b for a, b in zip(power, (opp_entity_sizes))]
        max_intermediary = max(intermediary_result)
        expected_result = [a/max_intermediary * params._W1 if max_intermediary else 0 for a in intermediary_result]

        # Now let's look what the tool would say
        real_result = vn.dependencyIndicatorBargainingPower(power, size, dao.EdgeType.INCOMING)
        self.assertAlmostEqual(real_result[0], expected_result[0])
        self.assertAlmostEqual(real_result[1], expected_result[1])

    # Test the calculation on a high-level (just input/output test).. Later on load config file for this?
    def test_mainTest(self):
        # CHECK PARAMS
        WR_V = params._WITHIN_RELATIONSHIP_V
        WE_V = params._WITHIN_ENTITY_V

        # MODIFY PARAMS TEMPORARILY (to control the test environment
        params._WITHIN_RELATIONSHIP_V = 3       # set to classic values
        params._WITHIN_ENTITY_V = 2             # set to classic values

        # COMPUTE RESULTS
        vn = vnqcontroller.VNQController()
        vn.g = self.g
        risk_params = [1, 1, 1, 1, 1, 1, 1, 1]
         # Does not test entity size computation!
        results = vn.run(risk_params, self.entity_sizes)
        ordered_results = tool.Graph.instance().order_results(vn.g, results)

        opp_entity_sizes = [self.integrate_entity_size(e) for e in self.entity_sizes]

        # COMPARE WITH CALCULATION BY HAND
        self.assertAlmostEqual(ordered_results[0], opp_entity_sizes[0]*1* params._W1+1* params._W2+(params._WR))                            # was checked by hand (should be OK)
        self.assertAlmostEqual(ordered_results[1], opp_entity_sizes[1]*0.7222222222* params._W1+1* params._W2+(params._WR))  # was checked by hand (should be OK)
        self.assertAlmostEqual(ordered_results[2], opp_entity_sizes[2]*1* params._W2+1* params._W1+(params._WR))        # was checked by hand (should be OK)

        params._WITHIN_RELATIONSHIP_V = WR_V
        params._WITHIN_ENTITY_V = WE_V

    def test_mainTest2(self):
         # CHECK PARAMS
        WR_V = params._WITHIN_RELATIONSHIP_V
        WE_V = params._WITHIN_ENTITY_V

        # MODIFY PARAMS TEMPORARILY (to control the test environment
        params._WITHIN_RELATIONSHIP_V = 3       # set to classic values
        params._WITHIN_ENTITY_V = 2             # set to classic values

        risk_params = [1, 1, 1, 1, 1, 1, 1, 1]

        vn = vnqcontroller.VNQController()
        vn.g = self.g2      # other graph (graph 2)
        results = vn.run(risk_params, self.entity_sizes)
        ordered_results = tool.Graph.instance().order_results(vn.g, results)

        opp_entity_sizes = [self.integrate_entity_size(e) for e in self.entity_sizes]
        # COMPARE WITH CALCULATION BY HAND
        self.assertAlmostEqual(ordered_results[0], opp_entity_sizes[0]*1* params._W1+1* params._W2+(params._WR))                            # was checked by hand (should be OK)
        self.assertAlmostEqual(ordered_results[1], opp_entity_sizes[1]*1* params._W1+1* params._W2+(params._WR))  # was checked by hand (should be OK)
        self.assertAlmostEqual(ordered_results[2], opp_entity_sizes[2]*1* params._W2+1* params._W1+(params._WR))        # was checked by hand (should be OK)


        params._WITHIN_RELATIONSHIP_V = WR_V
        params._WITHIN_ENTITY_V = WE_V

    #_WITHIN_ENTITY_V = 2  #Std. V being used for comparing the best alternatives of each relationship of an entity

    if __name__ == '__main__':
        unittest.main()
