from app import tool
from controller import vnqcontroller
from model import dao

__author__ = 'patrick'

import networkx as nx
from itertools import repeat

import vod.configuration as config                  # LOADS ALL THE PARAMETERS RELEVANT FOR BOTH CASES!
from vod.configuration import pound                 # Makes pound function accessible

###################################################################################################################################
# RECOMMENDATION: Also see FAQ (and other information) provided in VNQ.py (the main file)
# DATA: See configuration.py
# PURPOSE OF THIS FILE: Create the graph from the data in configuration.py and execute the VNQ computation
#
# Case/Scenario: Video on Demand (VoD) stream from NY, USA to London, UK in HD; Side payments-based transmission chain
###################################################################################################################################

helper = tool.Graph.instance()

###################################################################################################################################
########################################################### BASIC GRAPH ###########################################################
###################################################################################################################################
#
# SETUP GRAPH with ENTITIES
#

g = nx.MultiDiGraph()
g.graph['name'] = 'VoD_SidePayments_Example'
g.graph['version'] = 0.1
g.add_node(0, name='EC')                                            # Create 1st node
g.add_node(1, name='Content provider / VoD Platform')               # Create 2nd node
g.add_node(2, name='Access NSP US')                                 # Create 3rd node
g.add_node(3, name='Transit NSP')                                   # Create 4th node
g.add_node(4, name='Access NSP UK')                                 # Create 5th node

#
# SETUP RELATIONSHIPS (DIFFERENT TO NO SIDE PAYMENTS CASE!)
#

# Sales of videos
g.add_path([0,1,0])                             # Bilaterally link EC and VoD Platform = 2 unidirected edges - V1+V2

# Side payments do the rest (network transmission):
g.add_path([1,2,1])                             # Bilaterally link VoD/content provider and Access NSP US (Service for side payment) - W1 and W2
g.add_path([1,3,1])                             # Bilaterally link VoD/content provider and Transit NSP (Service for side payment) - X1 and Y2
g.add_path([1,4,1])                             # Bilaterally link VoD/content provider and Access NSP UK (Service for side payment) - Y1 and Y2

# Internet access business (separate business case)
# (just added, because it may be unrealistic from today's perspective to assume that customers can only use purchased service)
g.add_path([0,4,0])                             # Z1 and Z2

#################################################################################################################################
########################################################### INSTANCES ###########################################################
#################################################################################################################################


####################################### PART V #######################################
### Description: EC <-> VoD/Content provider
####################################### PART V #######################################

#----------------------------------------------------
# V1: VoD -> EC (Video service)
#----------------------------------------------------
#ASSUMPTION: The estimate will include the average_overall_transmission_costs already

vod_ec_list = []
for p in config.vod_prices_classic:
    vod_ec_list.append(dao.RelationshipInstance('vod_to_ec_classic', p, config._vod_cost_lv * p, 0, config._dep_fung_vod_ec))

#Substitutes: Monthly rental services
for p in config.vod_prices_flat:
    vod_ec_list.append(dao.RelationshipInstance('vod_to_ec_flat', p, config._vod_flat_cost_lv * p, 0, config._dep_fung_vod_ec))

print("VoD profit Nowtv: " + str(pound(3.49) - config._vod_cost_lv * config.vod_nowtv_price))
print("VoD profit Netflix: " + str(config.vod_netflix_price - config._vod_flat_cost_lv * config.vod_netflix_price))

# Add to graph
helper.safely_add_instances(g, 1, 0, 0, vod_ec_list)    # How many instances are required purchasing the data in a certain quality? i.e. here distribution of customers to providers

#----------------------------------------------------
# V2: Edge EC -> VoD: $ (not other costs, full fungibility)
#----------------------------------------------------

# Idea: Distribute ECs to Providers
# As there are more ECs than providers -> repetition of provider offer in the payment alternative
# NOTE: Currently the repetition concept has no relevant effect. It has an effect whenever loyalty regimes are tested in the future,
#   esp. with inhomogeneous customer groups. The hook for such tests has already been created.
repetition = tool.InputData.instance().spread_input(config._number_of_EC_subscribers, config.vod_prices)

paymentsToVoD = []
for k in range(0, len(config.vod_prices)):         # For every VoD / content provider player
    temp = config.vod_prices[k]
    paymentsToVoD.extend(repeat(dao.RelationshipInstance('ec_to_vod', temp, 0, 0, config._dep_fung_payment), repetition[k]))

# Add to graph
helper.safely_add_instances(g, 0, 1, 0, paymentsToVoD)

####################################### PART W #######################################
### Description: VoD <-> Access NSP US
####################################### PART W #######################################


#----------------------------------------------------
# W1: VoD -> Access NSP (Payment)
#----------------------------------------------------

vod_access_list = []
for p in config.us_access_prices_transitscheme:
    vod_access_list.append(dao.RelationshipInstance('vod_to_access_ps', (p), 0, 0, config._dep_fung_payment)) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).

# Add to graph
helper.safely_add_instances(g, 1, 2, 0, vod_access_list)

#----------------------------------------------------
# W2: Access NSP -> VoD (Service)
#----------------------------------------------------

access_vod_list = []
for p in config.us_access_prices_transitscheme:
    access_vod_list.append(dao.RelationshipInstance('access_to_vod', (p), (p*config._nsp_cost_lv), 0, config._dep_fung_US_access )) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).

helper.safely_add_instances(g, 2, 1, 0, access_vod_list)

####################################### PART X #######################################
### Description: VoD <-> Transit NSP
####################################### PART X #######################################

#----------------------------------------------------
# X1: VoD -> Transit NSP (Payment)
#----------------------------------------------------

vod_transit_payment_list = []
for p in config.classical_transit_prices:
    vod_transit_payment_list.append(dao.RelationshipInstance('vod_to_transit_ps', (p), 0, 0, config._dep_fung_payment)) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).

vod_cdn_payment_list = []
for p in config.cdn_prices:
    vod_cdn_payment_list.append(dao.RelationshipInstance('vod_to_transit_ps', (p), 0, 0, config._dep_fung_payment))

# Add to graph
helper.safely_add_instances(g, 1, 3, 0, vod_transit_payment_list)
helper.safely_add_instances(g, 1, 3, 0, vod_cdn_payment_list)

#----------------------------------------------------
# X2: Transit NSP -> VoD (Service)
#----------------------------------------------------

transit_vod_list = []
for p in config.classical_transit_prices:
    transit_vod_list.append(dao.RelationshipInstance('transit_to_vod_ps', (p), (p*config._nsp_cost_lv), 0, config._dep_fung_transit )) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).

transit_cdn_vod_list = []
for p in config.classical_transit_prices:
    transit_cdn_vod_list.append(dao.RelationshipInstance('transit_to_vod_ps', (p), (p*config._nsp_cost_lv), 0, config._dep_fung_transit)) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).

helper.safely_add_instances(g, 3, 1, 0, transit_vod_list)
helper.safely_add_instances(g, 3, 1, 0, transit_cdn_vod_list)

####################################### PART Y #######################################
### Description: VoD <-> Access NSP UK
####################################### PART Y #######################################

#----------------------------------------------------
# Y1: VoD -> Access NSP UK (Payment)
#----------------------------------------------------

vod_accessuk_payment_list = []
for i in range(0,config._number_of_accessUKplayers,1):
    vod_accessuk_payment_list.append(dao.RelationshipInstance('vod_to_accessuk_ps', (config._transit_movie_price), 0, 0, config._dep_fung_payment)) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).

# Add to graph
helper.safely_add_instances(g, 1, 4, 0, vod_accessuk_payment_list)

#----------------------------------------------------
# Y2: Access NSP UK -> VOD (Service)
#----------------------------------------------------

accessuk_vod_list = []
for i in range(0,config._number_of_accessUKplayers,1):
    accessuk_vod_list.append(dao.RelationshipInstance('accessuk_to_vod_ps', (config._transit_movie_price), (config._transit_movie_price*config._nsp_cost_lv), 0, config._dep_fung_UK_access_termination )) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).

helper.safely_add_instances(g, 4, 1, 0, accessuk_vod_list)


####################################### PART Z #######################################
### Description: Internet access UK (separate business)
####################################### PART Z #######################################

#----------------------------------------------------
#Z1 - money (good fungibility, no costs)
#----------------------------------------------------

# WARNING UPDATE COUNTER number_of_accessUK_players above if you update this list!

# Idea: Distribute ECs to Providers
# As there are more ECs than providers -> repetition of provider offer in the payment alterantive
repetition = tool.InputData.instance().spread_input(config._number_of_EC_subscribers, config.uk_access_prices)

ec_access_list = []
for k in range(0, len(config.uk_access_prices)):         # For every VoD / content provider player
    temp = config.uk_access_prices[k]
    ec_access_list.extend(repeat(dao.RelationshipInstance('access_to_ec', temp, 0, 0, config._dep_fung_payment), repetition[k]))

# Add the instances to the relationship of the graph
# Node 4: Access NSP UK; Node 0: EC
helper.safely_add_instances(g, 0, 4, 0, ec_access_list)

#----------------------------------------------------
#Z2 - Internet access (monthly contract)
#----------------------------------------------------

access_ec_list = []
for p in config.uk_access_prices:
    access_ec_list.append(dao.RelationshipInstance('access_to_ec', p, config._nsp_cost_lv * p, 0, config._dep_fung_accessuk_ec))

# Add to the graph
#access_ec_list = [access_ec1, access_ec2, access_ec3, access_ec4, access_ec5, access_ec6, access_ec7, access_ec8, access_ec9, access_ec10, access_ec11]
helper.safely_add_instances(g, 4, 0, 0, access_ec_list)


###################################################################################################################################
########################################################### COMPUTATION ###########################################################
###################################################################################################################################

vn = vnqcontroller.VNQController()
vn.setGraph(g)
#vn.g = g

#print(g.edges())

#print(g.nodes())
risk_params = [1, 1, 1, 1, 1]  # WE DO NOT HAVE ANY DATA ON THIS -> IGNORE FOR NOW AND SET ALL TO 1

results = vn.run(risk_params, config.entity_sizes)
#ordered_results = tool.Graph.instance().order_results(vn.g, results)
#vn.results(ordered_results)
results = vn.run(risk_params, config.entity_sizes)
#ordered_results = tool.Graph.instance().order_results(vn.getGraph(), results)
#vn.results(ordered_results)
vn.results(results)

#print(ordered_results)

###################################################################################################################################
########################################################### CONCLUSIONS ###########################################################
###################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
