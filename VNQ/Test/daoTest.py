from model import dao

__author__ = 'patrick'

import unittest


class RelationshipInstanceTestCase(unittest.TestCase):
    def test_utilityTest(self):
        name = 'TestName'
        value = 2.5
        operation_costs = 1.0
        investment_costs = 1.0
        fungibility_dep = 0.9

        i = dao.RelationshipInstance(name, value, operation_costs, investment_costs, fungibility_dep)

        #Correction factor should not be present by now -> plain utility equals normal utility and has the specified form
        expectedValue = (value - operation_costs - investment_costs) * (1-fungibility_dep)
        self.assertAlmostEqual(i.utility(), expectedValue)
        self.assertAlmostEqual(i.utility(), i.plainUtility())

        #Now set correction factor
        correction = 0.9
        i.setCorrection(correction)
        self.assertAlmostEqual(i.plainUtility(), expectedValue)
        self.assertAlmostEqual(i.utility(), expectedValue * correction)


if __name__ == '__main__':
    unittest.main()
