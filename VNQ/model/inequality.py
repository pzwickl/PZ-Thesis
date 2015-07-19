from abc import ABCMeta, abstractmethod
import math

from app import params, tool

from model import dao, reporting
from model.pattern import Singleton


@Singleton
class GiniAlgorithm():
    #HELPER
    def base_gini(self, data_list, v):
        overall_utility = sum(data_list)      # TODO: Cope with negative and positive utilities in list at the same time

        if overall_utility == 0:
            return params._ONLY_ONE_RELATIONSHIP_INEQUALITY
        gini = 0
        for u in [float(u) for u in data_list]:
            p2 = math.pow(u / overall_utility, v)
            gini += p2
        return gini

#PREREQUISITE: All information is captured in a networkx MultiDiGraph
class InequalityMeasure(object):
    __metaclass__ = ABCMeta

    #Calculates the inequality within an entity, i.e., among its relationships
    @abstractmethod
    def inequality_within_entity(self, node):
        pass

        #Calcualtes inequality within an entity, but scaled according the entity size

    #def scaledInequalityWithinEntity(self, node):
    #    pass

    #Calculates inequality within a relationship, i.e., among its instances
    #Parameter v is used for overweighting high utility alternatives (sic!) in this case, while this does
    #absolutely not apply to entityInequality!
    @abstractmethod
    def inequality_within_relationship(self, node, edgeNo, v):
        pass

    #Calculates a correction factor from the dependency of alternatives \delta_{in/out}
    #The better the alternatives to one one's offer, the lower the value of the relationship in general
    #This factor is, thus, used to lower the utility whenever necessary.
    @abstractmethod
    def correction_factor(self, nodeNo, edgeNo, v):
        pass

class Gini(InequalityMeasure):
    #static attributes

    def __init__(self, g, edgeType):
        if g is None or edgeType is None:
            raise TypeError('G and edgeType need to be set.')

        self.g = g

        self.edgeType = edgeType  # Incoming or outgoing edges to be considered
        self.graphHelper = tool.Graph.instance()  # Assist in the calculation process.. static nature
        #self.overallSize = self.size()  # 'Worth' of value network, i.e., sum of utilities


    def inequality_within_entity(self, node):
        utilities = self.graphHelper.relationship_utilities(self.g, node, self.edgeType)
        #utilities = self.relationshipUtilitiesPerEntity(node)
        if utilities is None:                                               # No edge seems to be defined
            self.file_report(node, self.edgeType)                      # Create a report for later analysis
            return params._NO_RELATIONSHIP_INEQUALITY                       # Return a default value

        v = params._WITHIN_ENTITY_V                                                #v ... always the std value 2 on this level!!
        return GiniAlgorithm.instance().base_gini(utilities, v)                                  # gini

    # WARNING: This script has to be called manually before being able to know the real utilities of a relationship (=edge)
    def correction_factor(self, node_no, edge_no, v):
        #utilities = plainUtilities(nodeNo, edgeNo)
        relationship = self.relationship_data(node_no, edge_no)
        gini_v = self.inequality_within_relationship(node_no, edge_no, v)
        self.graphHelper.set_instance_correction(relationship, [gini_v] * len(
            relationship[params._VALUES]))  #set the values to affect utility calculation

    #return gini

    #Relationship inequality is calculated and reflected in the utilities of best alternatives
    #PLEASE NOTE: utilities of all are updated in order to allow simple access, but this is redundant information
    #Customized over- or underweighting of inequality for specific groups (factor v)
    def inequality_within_relationship(self, node_no, edge_no, v):
        relationship = self.relationship_data(node_no, edge_no)
        utilities = self.graphHelper.plain_instance_utilities(relationship)
        gini = GiniAlgorithm.instance().base_gini(utilities, v)  # v may vary here due to testes strategy
        return gini

    def file_report(self, node_no, edge_type):
        report = reporting.NoEdgeReport(node_no, edge_type)
        reporting.ReportManager.registerReport('Node'+(str(node_no)+'Type'+str(edge_type)), report)

    def relationship_data(self, node_no, edge_no):
        if self.edgeType == dao.EdgeType.INCOMING:
            relationship = self.graphHelper.incoming_edge_data(self.g, node_no, edge_no)
        else:
            relationship = self.graphHelper.outgoing_edge_data(self.g, node_no, edge_no)
        return relationship


