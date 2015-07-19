#import pprint
from enum import Enum
#sudo pip install enum

class InconsistencyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class EdgeType(Enum):
    INCOMING = 1
    OUTGOING = 2


class RelationshipInstance(object):
    #value = 0.0
    #operation_costs = 0.0
    #investment_costs = 0.0

    #fungibility_dep = 0.0	#corresponds to delta_6 (d6)

    #correction = 0.0 		#corresponds to din/dout (needs to be externally calculated)

    def __eq__(self, other):
        return (isinstance(other, RelationshipInstance) and self.name == other.name and self.value == other.value and self.operation_costs == other.operation_costs and self.investment_costs == other.investment_costs and self.fungibility_dep == other.fungibility_dep and self.correction == other.correction)

    def __init__(self, name, value, operation_costs, investment_costs, fungibility_dep):
        self.name = name
        self.value = value
        self.operation_costs = operation_costs
        self.investment_costs = investment_costs
        self.fungibility_dep = fungibility_dep  # corresponds to delta_6 (d6)
        self.correction = 1.0  # corresponds to din/dout (needs to be externally calculated) // Weighted gini of the relationship -> used for modifying utility of the best

    # Sets the correction factor
    # Explanation: A factor that relativize the utility of each relationship (= business interaction)
    #   based on the computation it faces. For example, the utility may theoretically be high (high volume etc.),
    #   but the competition (due to rivalry, substitution, market entrance, ...) may be high. This factor is used
    #   for reflecting such effects.
    def setCorrection(self, correction):
        self.correction = correction

    #Utility of a relationship instance
    #DO NOT use when comparing with other instances -> use for comparison of relationships or entities
    def utility(self):
        return self.plainUtility() * self.correction  #TODO: CHECK WHETHER THIS IS CORRECT WITH CORRECTION

    #USAGE: Use best instance.utility to retrieve: U(1) * (1-(1-gini})) where (1-gini) = d_{in/out}
    #Please note that the (1-correction) is wrong as in the paper (1-(1-gini}) is used,
    #due to interpretetability of individual factors)

    #Ignores correction factor, which is useful for the computation of the correction itself
    #Always used when comparing instance patterns
    #Never used when comparing relationship patterns (refer to best instance + utility function)
    def plainUtility(self):
        return (self.value - self.operation_costs - self.investment_costs) * (1 - self.fungibility_dep)
        #test = RelationshipInstance('test', 2, 1)
        #print test