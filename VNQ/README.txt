################################################################################################################
# GENERAL INFORMATION
# This calculates value network dependencies on the basis of
#   Zwickl, P., Reichl, P., & Ghezzi, A. (2011). On the Quantification of Value Networks:
#       A Dependency Model for Interconnection Scenarios (Vol. 6995, pp. 63-74).
#       Presented at the Proceedings of the 7th International Workshop on Advanced Internet Charging and QoS technology (ICQT'11).
#   Zwickl, P., & Reichl, P. (2012). An Instance-Based Approach for the Quantitative Assessment of Key Value Network Dependencies.
#       Presented at the NETWORKING 2012 Workshops.
#   Zwickl, P., & Reichl, P. (2013). Graph-Theoretic Roots of Value Network Quantification (Vol. 8115, pp. 282-286).
#       Presented at the Proceedings of 19th EUNICE/IFIP WG 6.6 International Workshop, Springer Berlin Heidelberg.
#
# This tool does not provide means for calculating risk factors or fungibilities. These factors have to be
# calculated with the help of other tools or estimated. Calculation suggestions are given in the papers above,
# and will be extended in the thesis of the author (to be published).
################################################################################################################

################################################################################################################
# PROCESS
# The calculation process requires a good timing in order to satisfy the dependencies and to avoid unncessary loops (raising the complexity).
# [1_ISL] Prepare the data on instance level. Thus, we prepare the values required in order to understand how valuable a relationship is based on
# the underlying instances

# [2_ESL] Calculate individual bargaining powers of entities without comparing them
# [2_ES] Calculate the entity sizes (another missing piece of information)
# [2_BP] Calculate the bargaining powers

# [3_RK] Risk indicators
# [3_FINAL] Bring it altogether to nosidepayments.py the bargaining power indicators on a vn_level

# In the post-processing only results are displayed.
################################################################################################################

################################################################################################################
# TECHNICAL BACKGROUND
# This tools used networkx for graphs. Many conversion are necessary for this case. Visualisation should though be easily extensible.
# Naming thus has to mix in notations used by networkx which are more graph-centric
# A node is an entity
# An edge is a relationship representing a business interaction
#
# The graph is automatically analysed for consistency during runtime while calculating the result (sic!),
# i.e., a lazy consistency verifier mechanism. Inconsistencies may lead to the stopping of the computation or
# the filing of error reports. These reports are of essential importance for interpreting the validity of results.
# Main pitfalls do not allow meanigful analysis interpretation - the graph needs to be fixed.
################################################################################################################

################################################################################################################
# INSTALLATION INSTRUCTIONS (if required)
# sudo pip install networkx OR locate .egg files (if not installed) and run:
# sudo easy_install [/path]/networkx-1.8.1-py2.6.egg
# sudo pip install numpy
# sudo pip install pprint
################################################################################################################

################################################################################################################
# CONFIGURATION
# Essential parameters are in the 'params.py' file. These include: _WR, _W1, _W2 and
# WITHIN_RELATIONSHIP_V, _WITHIN_ENTITY_V

################################################################################################################

################################################################################################################
# LICENCE
# [To be added later]
################################################################################################################

################################################################################################################
# CONTACT: patrick.zwickl (at) univie.ac.at
# (University of Vienna, Faculty of Computer Science, Cooperative Systems Group)
################################################################################################################

################################################################################################################
# SHORT FAQ
# Can entities (nodes) take arbitrary numbers and names?
#   Names: Yes (We recommend fitting names)
#   Numbers: Start with 0 and increment (e.g., avoid having nodes with numbers 0,1,4 only)
# What are relationships and (relationship) instances?
#   Instances refer to relationship instances. Relationships are atomic unidirectional business interactions, e.g., selling a video stream service to a customer (a second relationship exists for the payment).
#   A relationship in the graph is represented as an edge. A relationship instance in the graph represents a property of the relationship describing the competitive market for providing this kind of business interaction.
#   A video stream may for example be provided by Netflix (one instance), Amazon (instance), and many others. These relationship instances may have different price and cost levels. Whenever they are substitutes that
#   have to be established (for the purpose of the VN) some investments may be necessary.
# How to add them to the graph?
#   Always use the helper to safely add instances (it makes sure nothing can be broken; it is difficult to keep a networkx graph with much information "clean" and consistent).
# How / Where to detect errors?
#   In the code, in a persisted file (e.g. XML or JSON) or using the automatic reporting system (when executing the computation some automatic checks are run that can detect whenever a node is not linked to the rest of the graph).
# What about other risk factors?
#   Those risk factors are not yet covered with automatisms and need to be inserted manually.
#   risk_params = [1, 1, 1, 1, 1]  # One entry per node (odered list). 1 means high risk dependency (bad for this entity) and 0 means the opposite (good)
#   We recommend using 0 or 1 in the case no data is available. In our examples, we prefer 1 to have a clear reference point around 1 (the maximum dependency in the VN is taken by one entity)
# How to execute the computation?
#   vn = vnq.VNQ()                                                              # create the computation object
#   vn.g = g                                                                    # add your graph
#   results = vn.run(risk_params, config.entity_sizes)                          # make the computation (and check if it runs through)
#   ordered_results = tool.Graph.instance().order_results(vn.g, results)        # order results to understand what result belongs to which node
#   vn.display(ordered_results)                                                 # print some outcomes
################################################################################################################
