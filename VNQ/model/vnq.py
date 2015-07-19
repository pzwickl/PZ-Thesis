from app.logger import log
from app import params, tool
from model import dao, inequality, reporting

class VNQ:
    def __init__(self):
        self.graphHelper = tool.Graph.instance()
        self.__g = None
        #self.g = g

    # Moderates the access to the graph
    def setGraph(self, g):
        self.__g = g

    def getGraph(self):
        if(self.__g == None):
            log.warning("You have not yet set the graph. This could lead to errors in the following.")
        return self.__g

    #@staticmethod
    def run(self, entity_sizes):
        #g = self.g
        ineqIN = inequality.Gini(self.__g, dao.EdgeType.INCOMING)
        ineqOUT = inequality.Gini(self.__g, dao.EdgeType.OUTGOING)

        power_indicators = []
        for ineq in [ineqIN, ineqOUT]:
            #Do hierarchical inequality measure works
            self.within_relationship_level(ineq)            # [1_ISL] Instance level, withinin relationship level: calc instance-utility
            power = self.entity_level(ineq)                 # [2_ESL]stop right before gini requires results from others

            #Calculate entity size
            if len(entity_sizes) > 0:                       # MANUAL entity size input
                log.warning("Entity size: Reverting to manual computation ...")     # User has overwritten the automatisms
                entity_sizes = self.normalize_manual_entity_sizes(entity_sizes)     # Make sure input sums to 1
                size = entity_sizes
            else:
                log.info("Entity size: Automatic computation...")                      # We investigate the business interaction volumes in the graph
                size = self.graphHelper.entity_sizes(self.__g, ineq.edgeType)     # [2_ES]

            # Call presentation of power and entity size results
            #ordered_powers = self.graphHelper.order_results(self.g, power)  # Order power
            #ordered_sizes = self.graphHelper.order_results(self.g, size)    # Order entity sizes
            #console.displayPowerSize(ordered_powers, entity_sizes)                            # Present

            #Make it a ready to use weighted indicator
            power_indicator = self.dependencyIndicatorBargainingPower(power, size, ineq.edgeType)   # [2_BP] integrates entity size and scales the result to a relative indicator
            power_indicators.append(power_indicator)

            log.info('---- phase completed ----')

        return power_indicators #, size]

    # Only updates values on instance level, i.e. calculates the correction factor for every instance in the graph, sets and stores it.
    def within_relationship_level(self, ineq):
        for node in [n for n, d in self.__g.nodes_iter(
                data=True)]:  # node should be number, so better not alternate. If so change to list index here
            temp = self.graphHelper.list_relationships(self.__g, node, ineq.edgeType)
            if temp is None:
                continue
            #print temp
            for edg in range(len(temp)):   # range(len(self.g.out_edges(node))):
                ineq.correction_factor(node, edg, params._WITHIN_RELATIONSHIP_V)
        return

    # Calculate within_entity effects for all entities
    def entity_level(self, ineq):
        power = []
        for node in [n for n, d in self.__g.nodes_iter(data=True)]:
            #print 'Node: ' + str(node)
            power.append(
                ineq.inequality_within_entity(node)) # = Gini required for bargaining power d1/2
                #ineq.scaledInequalityWithinEntity(node))  # = Bargaining power d1/2 with entity size (originally d7/d8)
        return power  # return the bargaining powers of each entity = node

    def dependencyIndicatorBargainingPower(self, power, size, edge_type):
        result = self.scale_power(power, size)                # add entity size to consideration
        power_indicator = self.normalize_power(result)              # make a relative dependency indicator d1 or d2
        #dep_indicator = self.opposite_of_power(power_indicator)   # We are currently measuring power
        weighted_indicator = self.weight_power(power_indicator, edge_type)     # Weight according weighting policy and parametrization
        return weighted_indicator

    #This integrates the entity size factor in the plain bargaining powers
    #Should be applied before making a relative dependency indicator for easier interpretation
    #NOTE TO DEVELOPERS: This is not the most efficient way of linking this information, but is used for clear separation.
    def scale_power(self, power, size):
        # TODO: Check whether (1-size[i]) is correct instead of size[i]
        result = []
        for i in range(len(power)):
            if size[i] > 0:
                #print("size: " + str(size[i]))
                #print("new size: " + str(1/size[i]))
                #print("old size: " + str(1-size[i]))                                            # TODO: Check the negative case
                result.append(power[i] * (1-size[i])) ## WAS: 1/size[i] OR size[i] ==(2014)==>  "* size[i]"
            else:
                result.append(power[i])
        return result

    def normalize_power(self, power):
        mp = max(power)
        if mp is 0:
            return [0] * len(power)
        return [p / mp for p in power]  # normalized as share of maximum inequality

    def weight_power(self, power, edge_type):
        if edge_type == dao.EdgeType.INCOMING:
            #print isinstance(power, int)
            return [(p) * params._W1 for p in power]      # Incoming edges = d1 = bargaining power of suppliers
        else:
            return [(p) * params._W2 for p in power]      # Outgoing edges = d2 = bargaining power of customers
    #    return [p * params._D for p in power]

    def risks(self, riskparams):
        #return riskparams # Todo: Potentially internalize risk parametrization later on
        return [r * params._WR for r in riskparams] # Todo: Potentially internalize risk parametrization later on
        # return config._WR + riskparams

    #NOTE TO DEVELOPERS: This is not the most efficient way of linking this information as it could easily be done more
    #efficiently in inequality classes etc., but this allows a good modification of the process sequence and thus a clearer structure.
    #You may change this whenever the performance is too low for your usage.
    def vn_level(self, power_indicators, rks_indicators):  # link it altogether (between_entity level)
        #check consistency (may not be problematic though if too much information)
        if len(power_indicators[0]) != len(rks_indicators):
            report = reporting.InputReport('Entered risk information is not aligned to the number of entities (=nodes).')
            reporting.ReportManager.registerReport('Risk', report)

        result = []
        #Multiply each entity's d_1 with d_2 and d_r values
        #All factors have already been weighted using w1, w2 and wr respectively
        for i in range(len(power_indicators[0])):
            result.append(power_indicators[0][i] + power_indicators[1][i] + rks_indicators[i])
            #result.append(power_indicators[0][i] * stateless._W1 + power_indicators[1][i] * stateless._W2 + stateless._WR * rks_indicators[i])
        return result

    # Create a relative representation of the entity size input
    def normalize_manual_entity_sizes(self, entity_sizes):
        overall_size = sum(entity_sizes)
        return [(float(s)/overall_size) if overall_size else 0 for s in entity_sizes]

    #def entity_size(self, node, power):
    #    self.graphHelper.relationshipUtilitiesPerEntity(self.g, node, self.edgeType)
