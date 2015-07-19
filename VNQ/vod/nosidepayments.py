import networkx as nx
from app import tool
from controller import vnqcontroller
from model import dao
from itertools import repeat

import vod.configuration as config              # LOADS ALL THE PARAMETERS RELEVANT FOR BOTH CASES
from vod.configuration import pound             # Makes pound function accessible

###################################################################################################################################
# RECOMMENDATION: Also see FAQ (and other information) provided in VNQ.py (the main file)
# DATA: See configuration.py
# PURPOSE OF THIS FILE: Create the graph from the data in configuration.py and execute the VNQ computation
#
# Case/Scenario: Video on Demand (VoD) stream from NY, USA to London, UK in HD; Classical transmission chain (= no side payments)
###################################################################################################################################

helper = tool.Graph.instance()

###################################################################################################################################
########################################################### BASIC GRAPH ###########################################################
###################################################################################################################################
#
# SETUP GRAPH with ENTITIES
#

g = nx.MultiDiGraph()
g.graph['name'] = 'VoD_NoSidePayments_Example'
g.graph['version'] = 0.1
g.add_node(0, name='EC')                                            # Create 1st node
g.add_node(1, name='Content provider / VoD Platform')               # Create 2nd node
g.add_node(2, name='Access NSP US')                                 # Create 3rd node
g.add_node(3, name='Transit NSP')                                   # Create 4th node
g.add_node(4, name='Access NSP UK')                                 # Create 5th node

#
# SETUP RELATIONSHIPS
#

g.add_path([0,1,0])                             # Bilaterally link EC and VoD Platform = 2 unidirected edges - A1+A2
g.add_path([1,2,1])                             # Bilateral link between VoD and Access NSP US - B1 + B2
g.add_path([2,3,2])                             # Bilateral link between Access NSP US and the Transit NSP  - C1 + C2
g.add_path([3,4,3])                             # Bilateral link between Transit NSP and the Access NSP Uk - D1 + D2
g.add_path([4,0,4])                             # Bilateral link between Access NSP UK and the EC - E1 + E2


#################################################################################################################################
########################################################### INSTANCES ###########################################################
#################################################################################################################################


####################################### PART E #######################################
### Description: Access NSP <-> EC
####################################### PART E #######################################

#----------------------------------------------------
#E1 - money (good fungibility, no costs)
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
#E2 - Internet access (monthly contract)
#----------------------------------------------------

access_ec_list = []
for p in config.uk_access_prices:
    access_ec_list.append(dao.RelationshipInstance('access_to_ec', p, config._nsp_cost_lv * p, 0, config._dep_fung_accessuk_ec))

# Add to the graph
#access_ec_list = [access_ec1, access_ec2, access_ec3, access_ec4, access_ec5, access_ec6, access_ec7, access_ec8, access_ec9, access_ec10, access_ec11]
helper.safely_add_instances(g, 4, 0, 0, access_ec_list)

####################################### PART D #######################################
### Description: Transit UK <-> Access NSP UK
####################################### PART D #######################################

# Let's assume the access NSP wants for termination something comparable to the transit fee, i.e., transit_movie_price

#----------------------------------------------------
# D1: Fee
#----------------------------------------------------

# Approach: Termination at equal value to transit service = same price

UKtermination_payment = []
for i in range(0,config._number_of_transit_players,1): # TODO: Align to _number_of_transit_players in subsequent updates
    UKtermination_payment.append(dao.RelationshipInstance('TransitToAccessUK', config._transit_movie_price, 0, 0, config._dep_fung_payment))

# Add to graph
helper.safely_add_instances(g, 3, 4, 0, UKtermination_payment)

#----------------------------------------------------
# D2: Termination service
#----------------------------------------------------
transit_alternatives_service = []
for i in range(0,config._number_of_accessUKplayers,1):
    transit_alternatives_service.append(dao.RelationshipInstance('AccessUKtoTransit', config._transit_movie_price, config._nsp_cost_lv*config._transit_movie_price, 0, config._dep_fung_UK_access_termination))

# Add to graph
helper.safely_add_instances(g, 4, 3, 0, transit_alternatives_service)

####################################### PART C #######################################
### Description: Access NSP US <-> Transit NSP
####################################### PART DC#######################################

#----------------------------------------------------
#C1: Money (high fungibility)
#----------------------------------------------------
#APPROACH: The cost of transit is the transit + a comparable fee for the termination, which is transitively paid by the access US NSP

# Classical Transit

# TODO: CARDINALITIES MAY NEED BETTER ALIGNMENT BASED ON SPREADING THE DEMAND/INPUT (see dedicated function)
all_prices = []
all_prices.extend(config.classical_transit_prices)
all_prices.extend(config.cdn_prices)
all_prices = [p + config._transit_movie_price for p in all_prices] # Pass a fee onwards in the chain for termination (only for this kind of graph setup!)

repetition = tool.InputData.instance().spread_input(config._number_of_accessUSplayers, all_prices);

#TRANSIT
transit_alternatives_payment = []
for k in range(0, len(config.classical_transit_prices)):         # For every VoD / content provider player
    temp = all_prices[k]                                 # Prices adjusted for this graph setup!
    transit_alternatives_payment.extend(repeat(dao.RelationshipInstance('accessUStoTransit_Transit', temp, 0, 0, config._dep_fung_payment), repetition[k]))

#CDN
cdn_list_payment = []
for k in range(len(config.classical_transit_prices), len(all_prices)):         # For every VoD / content provider player
    temp = all_prices[k]                                  # Prices adjusted for this graph setup!
    cdn_list_payment.extend(repeat(dao.RelationshipInstance('accessUStoTransit_CDN', temp, 0, 0, config._dep_fung_payment), repetition[k]))

#for i in range(0,config._number_of_accessUSplayers,1):
#    transit_alternatives_payment.append(dao.RelationshipInstance('accessUStoTransit', 2*config._transit_movie_price, 0, 0, 0.0))

#cdn_list_payment = config.cdn_list_payment # For each CDN create an instance; select or multiply in the case this needs to be changed

#cdn_list_payment = []
#for p in config.cdn_prices:
#    cdn_list_payment.append(dao.RelationshipInstance('accessUStoTransit_CDN', p+config._transit_movie_price, 0, 0, 0.0))

# Add to graph
helper.safely_add_instances(g, 2, 3, 0, transit_alternatives_payment) # Classical transit
helper.safely_add_instances(g, 2, 3, 0, cdn_list_payment) # CDN

#Private Peering substitute
# TODO

#Public Peering not-competitive according to Dr. Peering, so ignored here

#----------------------------------------------------
#C2: Transit services
#----------------------------------------------------

transit_alternatives_service = []

for p in config.classical_transit_prices:
    transit_alternatives_service.append(dao.RelationshipInstance('TransitToAccessUS_Transit', p+config._transit_movie_price, (config._nsp_cost_lv*p + config._transit_movie_price), 0, config._dep_fung_transit))

cdn_list_service = []
for p in config.cdn_prices:
    cdn_list_service.append(dao.RelationshipInstance('TransitToAccessUS', (p + config._transit_movie_price), (config._transit_movie_price + config._nsp_cost_lv*p), 0, config._dep_fung_transit))

# Add to graph
helper.safely_add_instances(g, 3, 2, 0, transit_alternatives_service) # Classical transit
helper.safely_add_instances(g, 3, 2, 0, cdn_list_service) # CDN (with and without known price)

#Cross-checking
print(str(config._nsp_cost_lv*config._transit_movie_price))
print(str(config.Akamai + config._transit_movie_price))
print("Transit profit example: " + str(2*config._transit_movie_price - (config._transit_movie_price + config._nsp_cost_lv*config._transit_movie_price)))
print("CDN profit example: " + str(config.CDN77 + config._transit_movie_price - (config._transit_movie_price + config._nsp_cost_lv*config.CDN77)))
print("CDN profit example: " + str(config.Akamai + config._transit_movie_price - (config._transit_movie_price + config._nsp_cost_lv*config.Akamai)))

#Private Peering substitute
# TODO

#Public Peering not-competitive according to Dr. Peering, so ignored here

####################################### PART B #######################################
### Description: Platform <-> Access NSP US
####################################### PART B #######################################
# Assumption: Business tariffs are upscaled access agreements with volume component.
# IS: Approach: Volume-based fee adjusted to competitive prices of carriers (taken from the consumer market prices)
#               + add every cost required for transit and termination (see parts below), i.e., external transit
# WAS: Approach: Use normal access fees (divided through share of ECs) + transit prices
#               + add every cost required for transit and termination (see parts below)

#rc_price = dollar(39.99)/share_of_EC_players
external_transit = 2*config._transit_movie_price                            # Transit payments to other providers (see C, D)

#----------------------------------------------------
# B1: VoD to Access NSP US (Payment)
#----------------------------------------------------

vod_access_list = []
for p in config.us_access_prices_transitscheme:
    vod_access_list.append(dao.RelationshipInstance('vod_to_access', (p + external_transit), 0, 0, config._dep_fung_payment)) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).

#vod_access1 = dao.RelationshipInstance('vod_to_access_rcn', (config.rc_transit+external_transit), 0, 0, config._dep_fung_payment) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).
#vod_access2 = dao.RelationshipInstance('vod_to_access_tcn', (config.tcn_transit + external_transit),  0, 0, config._dep_fung_payment)
#vod_access3 = dao.RelationshipInstance('vod_to_access_verizon', (config.verizon_transit + external_transit), 0, 0, config._dep_fung_payment)
#vod_access_list = [vod_access1, vod_access2, vod_access3]

# Add to graph
helper.safely_add_instances(g, 1, 2, 0, vod_access_list)

#----------------------------------------------------
# B2: Access NSP to VoD (Service)
#----------------------------------------------------

access_vod_list = []
for p in config.us_access_prices_transitscheme:
    access_vod_list.append(dao.RelationshipInstance('access_to_vod', (p + external_transit), (external_transit+ (p*config._nsp_cost_lv)), 0, config._dep_fung_US_access )) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).

#access_vod1 = dao.RelationshipInstance('access_to_vod_rcn', (config.rc_transit+external_transit), (external_transit+(config.rc_transit*config._nsp_cost_lv)), 0, config._dep_fung_access_vod ) # 2 times Transit paid for termination and acatually Transit. Third payment is to itself (so margin is kept).
#access_vod2 = dao.RelationshipInstance('access_to_vod_tcn', (config.tcn_transit + external_transit),  (external_transit + (config.tcn_transit*config._nsp_cost_lv)), 0, config._dep_fung_access_vod)
#access_vod3 = dao.RelationshipInstance('access_to_vod_verizon', (config.verizon_transit + external_transit), (external_transit + (config.verizon_transit*config._nsp_cost_lv)), 0, config._dep_fung_access_vod)
#access_vod_list = [access_vod1, access_vod2, access_vod3]

print("Access NSP US profit RCN: " + str((external_transit+config.rc_transit) - (external_transit+(config.rc_transit*config._nsp_cost_lv))))
print("Access NSP US profit TCN: " + str((config.tcn_transit + external_transit) - (external_transit+(config.tcn_transit*config._nsp_cost_lv))))


# Add to graph
helper.safely_add_instances(g, 2, 1, 0, access_vod_list)

#average_overall_transmission_costs = (config.rc_transit + config.tcn_transit + config.verizon_transit)/3.0 + external_transit

# INFO: The listed substitutes would be realistic for private purposes, but not for business
#vod_access4 = dao.RelationshipInstance('vod_to_access_repwireless', dollar(40.00)/usages, COSTS, 0, 0.8)
#vod_access5 = dao.RelationshipInstance('vod_to_access_millenicom', dollar(89.99)/1, COSTS, 0, 0.8)
#vod_access6 = dao.RelationshipInstance('vod_to_access_ATT', dollar(120)/1, COSTS, 0, 0.8) # only 20 GB, but rounded to 1 usage
#vod_access7 = dao.RelationshipInstance('vod_to_access_Verizon', dollar(190)/1, COSTS, 0, 0.8) # only 20 GB, but rounded to 1 usage
#vod_access8 = dao.RelationshipInstance('vod_to_access_Verizon', dollar(109)/usages, COSTS, 0, 0.8) # only 20 GB, but rounded to 1 usage

####################################### PART A #######################################
### Description: EC <-> VoD Platform / Content provider
####################################### PART A #######################################

#----------------------------------------------------
# A1: Edge VoD to EC: Video service (margin at X %, fungibility is 0.2, thus. dependency from fungibility 0.8)
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
# A2: Edge EC to VoD: $ (not other costs, full fungibility)
#----------------------------------------------------

# Theoretically the outnumbering of ECs is irrelevant, so we could create it symmetrically.
# But the quantification may be extended / advanced in the future. This is the safe variant here.
# TODO: Non-linearly split demand
# TODO: Align to other EC usages such as for Internet access in UK
# There is a new function in tool.py, which can be used for such purposes

# Idea: Distribute ECs to Providers
# As there are more ECs than providers -> repetition of provider offer in the payment alterantive
repetition = tool.InputData.instance().spread_input(config._number_of_EC_subscribers, config.vod_prices)

paymentsToVoD = []
for k in range(0, len(config.vod_prices)):         # For every VoD / content provider player
    temp = config.vod_prices[k]
    paymentsToVoD.extend(repeat(dao.RelationshipInstance('ec_to_vod', temp, 0, 0, config._dep_fung_payment), repetition[k]))

# Add to graph
helper.safely_add_instances(g, 0, 1, 0, paymentsToVoD)

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
#ordered_results = tool.Graph.instance().order_results(vn.getGraph(), results)
#vn.results(ordered_results)
vn.results(results)
#print(ordered_results)

###################################################################################################################################
########################################################### CONCLUSIONS ###########################################################
###################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
print("\nSome Interpretations:")
print("CDNs have higher absolute profits than transit NSPs")
#print("ECs highly dependent, but market size substantially lowers dependency, i.e., increase of power uptake.")
