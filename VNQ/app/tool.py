#import json
#import make_json_serializable
#requires jsonpickle
#	pip install -U jsonpickle
import pickle

import jsonpickle
#import inequality
import pprint
from app import params
from model import dao
import numpy
from model.pattern import Singleton


#Needs to be called/triggered outside

@Singleton
class Graph(object):
    #TODO: Maybe replace EXCEPTION by IF THEN or equivalent

    def __init__(self):
        #self.G = G
        return

    #_instance = None
    #def getInstance():
    #    if _instance is None
    #        _instance = GraphHelper()
    #    return _instance

    #def setupEdges(self, g):
    #    for node in self.nodesAsList(g):
    #        relationships = g.out_edges([node], data=True)
    #        for data in [data for i, o, data in relationships]:
    #            data[params._VALUES] = []


    #def safely_bilaterally_add_instances(self, g, from_node_no, from_edge_no, to_node_no, to_edge_no, instance_list):
    #    edge_type = dao.EdgeType.OUTGOING
    #    success = self.safely_add_instances(g, from_node_no, from_edge_no, edge_type, instance_list)
    #    edge_type = dao.EdgeType.INCOMING
    #    success = success and self.safely_add_instances(g, to_node_no, to_edge_no, edge_type, instance_list)
    #    return success

    # edge_no: Number of outgoing edge from from_node to to_node (not the sequence number of all edges!)
    def safely_add_instances(self, g, from_node_no, to_node_no, edge_no, instance_list):
        if instance_list is None:
            return

        #rel = [edge for edge in g.out_edges([from_node_no], data=True) if edge[1] == to_node_no]
        relationships = [d for [i, o, d] in g.out_edges([from_node_no], data=True) if o == to_node_no]
        if relationships is None or len(relationships) <= edge_no:         # For safety reason relationships is intentionally None, but this is not useful for setting it
            raise IndexError('The relationship (=edge) does not yet exist. Please, create beforehand. ')

        edge = relationships[edge_no]
        if not params._VALUES in edge or edge[params._VALUES] is None:
            temp = []
        else:
            temp = edge[params._VALUES]               # create list for relationship instances

        temp = Data.instance().add(temp, instance_list)     # add instances (or list of instances)
        edge[params._VALUES] = temp                         # store it

        #g.out_edges([node_no], data=True)[edge_no][2][params._VALUES] = temp

        #now cross-validate
        if not instance_list is list:
            instance_list = [instance_list]         # for measuring th length

        fresh_relationships = [d for i,o,d in g.out_edges([from_node_no], data=True) if o==to_node_no]      # pull things again from the graph to verify
        if not fresh_relationships is None and len(fresh_relationships[edge_no]) == len(instance_list):
            return True
        else:
            return False


    # This is the central method for creating edge data in the graph (please, use edge and node addition from networkx before, as illustrated in test.py)
    # This method decouples the access to the graph and thus assures more consistent data
    # Can cope with non-existent data structures to large extent (that's why directly accessing is not preferable)
    # Return: True if addition has been successful and False otherwise
    # edge_type: Defines the type of edge to be found and modified (based on node_no and edge_no within graph g)
    # instance_list: This is the data to be added (may be  list or a single Relationship Instance object)
    def old_safely_add_instances(self, g, node_no, edge_no, edge_type, instance_list):
        if instance_list is None:
            return

        relationships = self.list_relationships(g, node_no, edge_type)
        if relationships is None or not relationships[edge_no]:         # For safety reason relationships is intentionally None, but this is not useful for setting it
            if edge_type is dao.EdgeType.INCOMING:
                g.out_edges([node_no], data=True)
                relationships = [d for i,o,d in g.out_edges([node_no], data=True)]       # Pick the unmodified data from the graph (same data structure without consistency check)
            else:
                relationships = [d for i,o,d in g.in_edges([node_no], data=True)]        # Pick the unmodified data from the graph (same data structure without consistency check)

        edge = relationships[edge_no]
        if not params._VALUES in edge or edge[params._VALUES] is None:
            temp = []
        else:
            temp = edge[params._VALUES]               # create list for relationship instances

        if not instance_list is list:
            instance_list = [instance_list]             # we expect a list, but we do not mind if not ;) -> so length can be checken in all cases

        debug = Data.instance()
        temp = Data.instance().add(temp, instance_list)     # add instances (or list of instances)
        #temp.extend(instance_list)                    # add instances (or list of instances)
        if edge_type == dao.EdgeType.OUTGOING:
            g.out_edges([node_no], data=True)[edge_no][2][params._VALUES] = temp
        else:
            g.in_edges([node_no], data=True)[edge_no][2][params._VALUES] = temp

        #now cross-validate

        fresh_relationships = self.list_relationships(g, node_no, edge_type)
        if not fresh_relationships is None and len(fresh_relationships[edge_no]) == len(instance_list):
            return True
        else:
            return False


    #def createEdgeData(self, g, node, ):
    #    edge_data = G.out_edges([node], data=True)
    #    for data in edge_data:
    #        data[params._VALUES] = []

        #edge_data[params._VALUES] = []
        #len (G.out_edges([node], data=True))

    #Return the edge data for all out. relationships or a specific outgoing relationship (supplier-side) of a node
    def outgoing_edge_data(self, g, node, edge_no=None):
        try:
            data_list = [d for i, o, d in g.out_edges([node], data=True)]  #Data is: G.out_edges([j],data=True)[i][2]
            self.consistency_check(data_list)
            if edge_no is None:
                return data_list                    # Return data for all edges
            else:                                   # Return for specific edge data only
                if len(data_list) is 0:
                    return None                     #Could be redundant path now
                else:
                    return data_list[edge_no]
            #return data_list
        #return G.out_edges([j],data=True)[i][2]
        except IndexError:
            return None  #print 'no edge defined'

    #Return the edge data for all incoming relationships or a specific outgoing relationship (supplier-side) of a node
    def incoming_edge_data(self, g, node, edge_no=None):
        try:
            data_list = [d for i, o, d in g.in_edges([node], data=True)]  #Data is: G.out_edges([j],data=True)[i][2]
            self.consistency_check(data_list)
            if edge_no is None:
                return data_list                    # Return data for all edges
            else:                                   # Return for specific edge data only
                if len(data_list) is 0:
                    return None                     #Could be redundant path now
                else:
                    return data_list[edge_no]
            #return data_list
        #return G.out_edges([j],data=True)[i][2]
        except IndexError:
            return None  #print 'no edge defined'

        #single in edge data

    #def incoming_edge_data(self, g, node, edge_no):
    #    temp = g.in_edges([node], data=True)
    #    if len(temp) is 0:
    #        return None
    #    return temp[edge_no][2]

    #single out edge data
    #def outgoingEdgeData(self, G, node, edge_no):
    #    temp = G.out_edges([node], data=True)
    #    if len(temp) is 0:
    #        return None
    #    return temp[edge_no][2]



    #ENTITY SIZE

    # Return: sum of entity sizes (= value network size)
    # g: graph to be analyzed
    # edge_type: considered edge_type (only one direction is calculated at a time)
    def size(self, g, edge_type):
        #for n in G.nodes:
        #For all nodes in G, list the relationships (in or out), nosidepayments.py the utility and sum them
        worth = 0

        #for node in [n for n, d in self.g.nodes_iter(data=True)]:
        worth2 = 0
        for node in self.list_nodes(g):
            #for node in self.G.nodes():
            relationships = self.list_relationships(g, node, edge_type)                                # Size for in/out parts
            #worth += sum([self.graphHelper.relationshipUtility(self.g, x) for x in relationships]) # If g is required, use this line
            #worth += sum([self.graphHelper.relationshipUtility(x) for x in relationships])
            if relationships is None:
                continue

            for rel in relationships:
                debug = self.relationship_utility(rel)
                worth2 += self.relationship_utility(rel)
            worth += sum(map(self.relationship_utility, relationships)) #cannot handle nonetypes
            #[add(x, 2) for x in [1, 2, 3]]
        return worth

    # Return: the size of all entities as a list
    # g: graph to be analyzed
    # edge_type: considered edge_type (only one direction is calculated at a time)
    def entity_sizes(self, g, edge_type):
        overall_size = self.size(g, edge_type)
        print "Overall size: " + str(overall_size)
        results = []
        for node in self.list_nodes(g):
            utilities = self.relationship_utilities(g, node, edge_type)         #TODO: CHECK WHETHER plain utilities SHOULD BE USED INSTEAD (DESIGN DECISION)
            if utilities is None or len(utilities) == 0 or overall_size == 0:
                results.append(0)
            else:
                Data.instance().add(results, sum(utilities)/overall_size) # append it whether one or more results are produced
                #results.extend(sum(utilities)/overall_size)
        return results


    #max(edge.y for node in path.nodes)

    # USAGE: FOR CORRECTION FACTOR COMPUTATION (can be called at all times)
    # Return: Uncorrected utilities (=plain utilities) of all relationship instances of an edge
    # edge_data: Contains the data for the single edge to be analyzed
    def plain_instance_utilities(self, edges_data):
        if edges_data is None:
            return None
        #debug = edges_data[params._VALUES]
        return [i.plainUtility() for i in edges_data[params._VALUES]]

    # USAGE: Always used when graph has been analyzed (correction factor is set according value distribution) and 'real' utility is required
    # Return: Uncorrected utilities (=plain utilities) of all relationship instances of an edge
    # edge_data: Contains the data for the single edge to be analyzed
    def instance_utilities(self, edges_data):
        if edges_data is None:
            return None
        return [i.utility() for i in edges_data[params._VALUES]]

    # Update all relationship instances utilities with the correction factor
    def set_instance_correction(self, edge_data, corrections):
        values = edge_data[params._VALUES]
        for i in range(len(corrections)):
            values[i].setCorrection(corrections[i])
            #values[i].correction = corrections[i]
        return

    def order_results(self, g, input):
        values = input[:]                                      # Make a copy of the input data (we will destroy it, so better do it)
        output = []
        nodes = [int(i) for i in g.nodes()]                     # all nodes to an int list

        while nodes:                                           # as long as there are elements in nodes
            nodes_index = numpy.argmin(nodes)                   # find node with lowest number
            nodes.pop(nodes_index)                              # remove it from the temporary list
            output.append(values[nodes_index])        # append result of minimum (first node) to ordered list
            values.pop(nodes_index)                            # keep result elements synced with nodes

        # Implementation was not robust enough w.r.t. unconventional numbering of nodes
        #ordered_results2 = values[:]                            # copy one by one .. no copy function available
        #for i in range(len(values)):
        #    nodes_index = g.nodes()[i]                          # get node number
        #    ordered_results2[int(nodes_index)] = values[i]      # set according node number
        #new_nodes = g.nodes()

        return output

    #def instanceUtilities(self, edge_data):
    #    return edge_data[params._VALUES]  #read attribute

    #def setInstanceUtilities(self, edge_data, list):
    #    edge_data[params._VALUES] = list  #add elements as graph attribute
    #    self.setRelationshipUtility(edge_data)  #find maximum
    #    return

    #def createEdgeData(self, node, edge_no, edge_type):
    #    if edge_type is dao.EdgeType.INCOMING:
    #        temp = G.in_edges([node], data=True)
    #    else:
    #        temp = G.out_edges([node], data=True)
#
    #    temp[edge_no][2] = dao.RelationshipInstance

     #   if len(temp) is 0:
     #       return None
     #   return temp[edge_no][2]


    #def addInstanceUtility(self, edges_data, instance):
    #    if (not edges_data[params._VALUES]):  #check if list empty
    #        edges_data[params._VALUES] = []  #add empty list
    #    Data.instance().add(edges_data[params._VALUES], instance)        # append to new instance to list
    #    #edges_data[params._VALUES].extend(instance)  #append to new instance to list
    #    if not params._BEST in edges_data or (edges_data[params._BEST] < instance.utility):  #Update maximum
    #        edges_data[params._BEST] = instance.utility
    #    #edge[_BEST] = max(i.utility for i in edge[_VALUES])	#find maximum
    #    return

    #def safelyAddInstanceUtility(self, edges_data, instance):


    #Not on edge_data basis
    #def updateUtility(self, nodeNo, edgeNo):


    #HELPERS

    def list_relationships(self, g, node, edgeType):
        if edgeType == dao.EdgeType.INCOMING:
            relationships = self.incoming_edge_data(g, node)  # already correct 'format'
        else:
            relationships = self.outgoing_edge_data(g, node)  # already correct 'format'
        return relationships
        #else:
        #    print 'test'

    def list_nodes(self, g):
        return [n for n, d in g.nodes_iter(data=True)]

    #Returns the utility of the best alternative (= RelationshipInstance) for an edge (stored in edge_data)
    def relationship_utility(self, edge_data):
        if not params._BEST in edge_data:
               # not edge_data[params._BEST]:  # Best is used for 'caching'
            self.set_relationship_utility(edge_data)
        return edge_data[params._BEST]

    #Returns the utility of the best alternative for each relationship (= edge) of an entity (=node)
    def relationship_utilities(self, G, node, edge_type):
        relationships = self.list_relationships(G, node, edge_type)
        if relationships == None:
            return None
        utilities = [self.relationship_utility(r) for r in relationships]
        #utilities = map(self.relationshipUtility, relationships)
        return utilities

    def set_relationship_utility(self, edge_data):
        #if len(edge_data[_VALUES]) == 0:
        #    raise IndexError('Data of edges (values, costs, etc.) not properly filled in.')
        debug = [i.utility() for i in edge_data[params._VALUES]]
        edge_data[params._BEST] = max([i.utility() for i in edge_data[params._VALUES]])  #find maximum
        #print 'bla'

    def consistency_check(self, results):
        if results is None:
            return

        erroneous = [a for a in results if not str(params._VALUES) in a]
        if len(erroneous) > 0 or len(results) == 0:
            response = 'At least ' + str(len(erroneous)) + ' edges have missing information, e.g., values, costs, etc.!'
            raise IndexError(response)

    #def relationshipAsAList(self, g, node, edgeType):
    #    if edgeType == dao.EdgeType.INCOMING:
    #        relationships = self.incomingEdgesData(g, node)  # already correct 'format'
    #    else:
    #        relationships = self.outgoingEdgesData(g, node)  # already correct 'format'
    #    return relationships

#@Singleton
#class Data(object):
#    # SCENARIO: A multitude of players, e.g., customers, are purchasing services from a handful of marketplace providers.
#    # APPROACH: Distribute the payments of the entire population to the individual players.
#    #   In other words, create many relationship instances sending money to every player.
#    # price_list, operation_cost_list, investment_cost_list: Price, cost tags by the providers (set by target of relationship)
#    # TODO: Replace linear assignment by something more sophisticated in the future
#    # population: The size of the "population" sending the resource/good/money/... (source of relationship)
#    # fungibility_list: Dependency from fungibiltiy for each resource exchanged (this covers substitute purchases)
#    def spreadDataOverPopulation(self, name, price_list, operation_cost_list, investment_cost_list, fungibility_list, population):
#        result = []
#        if population > len(price_list):
#            for i in range(0,len(price_list)):
#                for j in range(0,population/len(price_list),1):
#                    result.add(dao.RelationshipInstance(name, price_list[i], operation_cost_list[i], investment_cost_list[i], fungibility_list[i]))
#        else:
#            # TODO: CHECK FOR EACH OFFER AN ITEM OR RATHER FOR POPULATION ONLY (IS BOTH A BIT STRANGE)
#            for i in range(0,len(price_list):
#                result.add(dao.RelationshipInstance(name, price_list[i], operation_cost_list[i], investment_cost_list[i], fungibility_list[i]))
#        return result

# NOTE: You can always use the networkx serialization instead!
@Singleton
class Persistence(object):

    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4)    # advanced printing purposes

    def fromJSON(self, fileName):
        data = self.readFile(fileName)
        print params._VISUAL_INLINE_MARKER + 'Loading the following JSON data for you:'
        self.pp.pprint(data)
        return jsonpickle.decode(data)

    def toJSON(self, fileName, G):
        data = jsonpickle.encode(G)
        self.writeFile(fileName, data)
        print params._VISUAL_INLINE_MARKER + 'Written to file {}.'.format(fileName)
        return

    #load from Bytestream file
    #usage: is called my main file to load graph to be analyzed
    def fromBytestream(self, filename):
        pkl_file = open(filename, 'rb')

        data = pickle.load(pkl_file)
        pprint.pprint(data)

        pkl_file.close()
        print params._VISUAL_INLINE_MARKER + 'Loading the following bistream data for you:'
        print data
        return data  #I am an object of G (typically)

    #if '_python_object' in dct:
    #return pickle.loads(str(dct['_python_object']))
    #return dct

    #persist as json whole graph to 'file'
    #usage: create script file with G of choice -> perist (+modify) -> load later when necessary
    def toBytestream(self, filename, G):
        output = open(filename, 'wb')

        # Pickle the list using the highest protocol available.
        pickle.Pickler(output, pickle.HIGHEST_PROTOCOL).dump(G)
        #spickle.dumps(G, output) #, pickle.HIGHEST_PROTOCOL)
        #pickle.dump(G, output, -1)

        output.close()
        return

    #print json.dumps(foo)  # "{u'name': u'sazpaz'}"
    #pass

    def writeFile(self, filename, data):
        f = open(filename, 'w')
        f.write(data)
        f.close()
        return

    def readFile(self, filename):
        f = open(filename)
        data = f.read()
        f.close()
        return data

@Singleton
class InputData(object):
    def spread_input(self, total_demand, prices):
        #print(prices)
        #print(total_demand)

        #TODO: What happens in the case the population is smaller or equal to the offers? For now add all with a single unit
        #More advanced customer assignment alogrithms may produce different results and may have to be changed here as well!
        if(total_demand <= len(prices)):
            return [1 for p in prices]

        return self.linearly_spread_input(total_demand, prices)

    def linearly_spread_input(self, total_demand, prices):
        #print(prices)
        #print(total_demand)
        share = int(total_demand/len(prices))       # creates the floor of it
        result = [share for p in prices]
        return result

    # TODO: NOT YET WORKING CORRECTLY!
    # demand minding loyalty as formulated in Reichl, P., Zwickl, P., Loew, C., & Maille, P. (2013). How Paradoxical Is the "Paradox of Side Payments?" Notes from a Network Interconnection Perspective (pp. 115-128). Presented at the Wired/Wireless Internet Communication, Springer.
    def demand_with_loyalty(total_demand, number_of_players, price, average_price):
        beta = (float(price) / average_price)
        #sigma = beta - 1.0/number_of_players*(beta*beta)
        #if beta >= 1:
        #    sigma = 1 - sigma
        #  return total_demand * sigma

        return total_demand*beta

#def all_demands_with_loyalty(total_demand, prices):
#    average_price = np.sum(prices)
#    number_of_players = len(prices)
#    result = []
#    for p in prices:
#        p.append(demand_with_loyalty(total, 3, 2, sum_price))


@Singleton
class Data(object):
    # Append or extend a list based on whether new_list is a list or just an item
    def add(self, base_list, new_list):
        if isinstance(new_list,list):
            base_list.extend(new_list)
        else:
            base_list.append(new_list)
            #result = base_list.add(new_list)
        return base_list
#CLass specifically designed to handle complex obj encoding
#class ComplexJSONEncoder(json.JSONEncoder):
#	def default(self, obj):
#		if isinstance(obj, complex):
#			return [obj.real, obj.imag]
#		# Let the base class default method raise the TypeError
#		return json.JSONEncoder.default(self, obj)

#t = nx.MultiDiGraph()  #directed graph, which allows multiple 'similar' edges between two nodes
#t.graph['name'] = 'DefaultGraphInequalityTest'
#t.graph['version'] = 0.1
#t.add_node(1, name='TestNode1')
#t.add_node(2, name='TestNode1')
#t.add_edges_from([(1, 2), (2, 1), (1, 2)])
#ntest1 = t.nodes()[0]
#ntest2 = t.nodes()[1]
#print t[ntest1][ntest2]
#edg = t.edges()[0]
#print t[1][2]
#t[1][2]['some'] = 'test'
#t[1][2]['name'] = 'myName'
#print t[1][2]
#edgies = t.edges(data=True)
#print edgies
#print edgies[0][1]


#G = None
#edgeType = None
#inequality.Gini(G, edgeType)
#print edg[2]
#edgAttr = 
#edgDict = edgAttr[1] #0 is name.. 1 is dictionary
#self, name, value, operation_costs, investment_costs, fugibility_dep, correction
#t[ntest1][ntest2][_VALUES] = dao.RelationshipInstance('firstinstance', 2.0, 0.3, 0.8, 0.6)
#print t[ntest1][ntest2]
#print 'blabla: '
#print t.nodes()
#a = t.edges(data=True)
#print a[0][2] # [_VALUES]
##print a[2][_VALUES]

