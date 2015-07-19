import networkx as nx

from app import params, tool
from model import dao



#class Test:
#	#def __setstate__():	#optional: to be sure we are using the correct version
#
#	def __init__(self, name):	#required for json serialization
#		self.name=name
#		return
#	
#	def testtest(self):
#		print "that works"
#		return

#Testrun
#t = Test("Test1")
#fileName = "/Users/patrick/OfficeCb/workspace/VNQAPP/test.bitstream"
#fileName2 = "/Users/patrick/OfficeCb/workspace/VNQAPP/test.json"
fileNameBIT = params._SAMPLE_JSON_FILE
fileNameJSON = params._SAMPLE_JSON_FILE

loader = tool.Persistence.instance()

t=nx.MultiDiGraph() #directed graph, which allows multiple 'similar' edges between two nodes
t.graph['name']='DefaultGraphConfigTest'
t.graph['version']=0.1
t.add_node(0, name='Node0')
t.add_node(1, name='Node1')
t.add_node(2, name='Node2')
t.add_path([0,1, 2])
t.add_path([1,2,1])
t.add_path([1,0])
#t.add_path([1,2,0])
print t.edges(data=True)

##### PUT THIS BLOCK IN A SPECIFIC CLASS?
helper = tool.Graph.instance()

# All connection to Node 0

test = dao.RelationshipInstance('between0and1_inandout', 4, 0, 0, 0.0)
helper.safely_add_instances(t, 0, 1, 0, test)   # Add single instance for the first edge between 0 and 1
helper.safely_add_instances(t, 1, 0, 0, test)   # Add single instance for the first edge between 1 and 0 (identical data here, thus same object will do)

# All new connections to Node 1 (outgoing)

no1_out1_inst1 = dao.RelationshipInstance('between0and1_inandout', 1, 0, 0, 0.0)
no1_out1_inst2 = dao.RelationshipInstance('between0and1_inandout', 0.9, 0, 0, 0.0)
no1_out1_inst3 = dao.RelationshipInstance('between0and1_inandout', 0.8, 0, 0, 0.0)
no1_out1 = [no1_out1_inst1, no1_out1_inst2, no1_out1_inst3]

helper.safely_add_instances(t, 1, 2, 0, no1_out1)   # Add single instance for the first edge between 1 and 2

no1_out2_inst1 = dao.RelationshipInstance('between0and1_inandout', 2, 0, 0, 0.0)
no1_out2_inst2 = dao.RelationshipInstance('between0and1_inandout', 1, 0, 0, 0.0)
no1_out2 = [no1_out2_inst1, no1_out2_inst2]
helper.safely_add_instances(t, 1, 2, 1, no1_out2)   # Add single instance for the second edge between 1 and 2

# ALl connections to Node 2 (outgoing)

no2_out1_inst1 = dao.RelationshipInstance('between0and1_inandout', 3, 0, 0, 0.0)
no2_out1_inst2 = dao.RelationshipInstance('between0and1_inandout', 1.5, 0, 0, 0.0)
no2_out1_inst3 = dao.RelationshipInstance('between0and1_inandout', 1.5, 0, 0, 0.0)
no2_out1 = [no2_out1_inst1, no2_out1_inst2, no2_out1_inst3]
helper.safely_add_instances(t, 2, 1, 0, no2_out1)   # Add single instance for the first edge between 2 and 1


#helper.setupEdges(t)                            # prepare edge data object for each edge available

#nodes = helper.nodesAsList(t)
#incoming_relationships = [helper.relationshipDataAsAList(t, node, dao.EdgeType.INCOMING) for node in nodes]
#outgoing_relationships = [helper.relationshipDataAsAList(t, node, dao.EdgeType.OUTGOING) for node in nodes]
######

#NOW SET VALUES ...
#Node 0

# NODE 0 -- INCOMING AND OUTGOING

#node_no = 0
#edge_no = 0

#no0_inst1 = dao.RelationshipInstance('between0and1_inandout', 4, 0, 0, 0.0)
#helper.old_safely_add_instances(t, node_no, edge_no, dao.EdgeType.INCOMING, no0_inst1)
#helper.old_safely_add_instances(t, node_no, edge_no, dao.EdgeType.OUTGOING, no0_inst1)    #identical object(s) as identical data in this example (not default case)

# NODE 1 -- OUTGOING
#edge_type = dao.EdgeType.OUTGOING
#node_no = 1
#edge_no = 0

#no1_out1_inst1 = dao.RelationshipInstance('between0and1_inandout', 1, 0, 0, 0.0)
#no1_out1_inst2 = dao.RelationshipInstance('between0and1_inandout', 0.9, 0, 0, 0.0)
#no1_out1_inst3 = dao.RelationshipInstance('between0and1_inandout', 0.8, 0, 0, 0.0)

#no1_out1 = [no1_out1_inst1, no1_out1_inst2, no1_out1_inst3]

#helper.old_safely_add_instances(t, node_no, edge_no, edge_type, no1_out1)

#edge_no = 1

#no1_out2_inst1 = dao.RelationshipInstance('between0and1_inandout', 2, 0, 0, 0.0)
#no1_out2_inst2 = dao.RelationshipInstance('between0and1_inandout', 1, 0, 0, 0.0)
#no1_out2 = [no1_out2_inst1, no1_out2_inst2]

#helper.old_safely_add_instances(t, node_no, edge_no, edge_type, no1_out2)

#edge_no = 2

#helper.old_safely_add_instances(t, node_no, edge_no, edge_type, [no0_inst1])    # now do the handshake and add what has been created by node 0 in the opposite direciton

# NODE 1 -- INCOMING

#edge_type = dao.EdgeType.INCOMING
#edge_no = 0

#helper.old_safely_add_instances(t, node_no, edge_no, edge_type, [no0_inst1])    # now do the handshake and add what has been created by node 0 in the opposite direciton

#edge_no = 1

#no1_in1_inst1 = dao.RelationshipInstance('between0and1_inandout', 3, 0, 0, 0.0)
#no1_in1_inst2 = dao.RelationshipInstance('between0and1_inandout', 1.5, 0, 0, 0.0)
#no1_in1_inst3 = dao.RelationshipInstance('between0and1_inandout', 1.5, 0, 0, 0.0)

#no1_in1 = [no1_in1_inst1, no1_in1_inst2, no1_in1_inst3]

#helper.old_safely_add_instances(t, node_no, edge_no, edge_type, no1_in1)

# NODE 2 -- OUTGOING (HANSHAKES ONLY)

#edge_type = dao.EdgeType.OUTGOING
#node_no = 2
#edge_no = 0

#helper.old_safely_add_instances(t, node_no, edge_no, edge_type, no1_in1)

# NODE 2 -- OUTGOING (HANSHAKES ONLY)

#edge_type = dao.EdgeType.INCOMING
#node_no = 2
#edge_no = 0

#helper.old_safely_add_instances(t, node_no, edge_no, edge_type, no1_out1)

#edge_no = 1
#helper.old_safely_add_instances(t, node_no, edge_no, edge_type, no1_out2)

#in_00 = inst4
#out_00 = inst4


#helper.createEdgeData(0) #create edge data for all edges of a node
#helper.addInstanceUtility(outgoing_relationships[0][0], inst4)
#helper.addInstanceUtility(incoming_relationships[0][0], inst4)



#outgoing_relationships[0][0]
#incoming_relationships[0][0] =

#Node 1

#helper.incomingEdgeData(t, node_no, edge_no)

#Interesting methods:
#def incomingEdgeData(self, G, node, edge_no):
#def setInstanceUtilities(self, edge_data, list): # if list
#def addInstanceUtility(self, edges_data, instance): # if one

loader.toJSON(fileNameJSON,t)
newObj = loader.fromJSON(fileNameJSON)
print newObj.graph['name'] #test whether we can access normally again


#Bytestream
#loader.toBytestream(fileNameBIT,t)
#newObj = loader.fromBytestream(fileNameBIT)
#print newObj.graph['name'] #test whether we can access normally again
#newObj.testtest()	#test whether we can access normally again
#print newObj.name 	
#JSON
#loader.toJSON(fileName2,t)
# loader.fromJSON(fileName2)
