import pprint
import networkx as nx
from app import params, tool
from model.vnq import VNQ # as VNQ
from model import reporting
from app.logger import log
from view.console import vnq
#import view.console.vnq


#######################################
# Please, see README.txt
#######################################

# TODO: Negative numbers not yet fully represented in the computation.
# TODO: Cleanup / Refactoring required


class VNQController:
    def __init__(self):
        self.loader = None
        #self.g = None                               # Graph .. redundant step #never forget self when assigning ;)
        self.pp = pprint.PrettyPrinter(indent=4)    # advanced printing purposes
        self.vnq_model = None
        self.setup()                                # creating basic loader and basic graph


        return

    # Set the graph
    # Pipes it through to the model
    def setGraph(self, g):
        #self.g = g
        self.vnq_model.setGraph(g)

    def getGraph(self):
        return self.vnq_model.getGraph()

    # Creates a base graph
    # Creates required tools
    def setup(self):
        #configure loader
        self.loader = tool.Persistence.instance()
        self.graphHelper = tool.Graph.instance()

        #CREATE BASE GRAPH
        #When using the loading functionalities, it will be overwritten
        self.vnq_model = VNQ()
        self.setGraph(nx.MultiDiGraph())  # directed graph, which allows multiple 'similar' edges between two nodes

        g = self.vnq_model.getGraph()
        g.graph['name'] = 'DefaultGraph'
        g.graph['version'] = 0.1
        g.add_node(1, name='TransitNSP')

        self.welcome()


        #self.g.node[1]

        #self.welcome()
        #welcome

        return

    # Welcome message
    # Points to view
    def welcome(self):
        vnq.VNQView.welcome()


    def configure(self, file):  #add parameters later
        log.info('Configuring the graph ...')

        self.setGraph(self.loader.fromJSON(file)) #
        self.pp.pprint(self.vnq_model.getGraph())
        node_list = self.graphHelper.list_nodes(self.vnq_model.getGraph())

        log.info(str(len(node_list)) + ' nodes detected (#):')

        for node in node_list:
            log.info('Node: #'+ node)
            #print params._VISUAL_INLINE_MARKER + params._VISUAL_INLINE_MARKER + '#' + node
        return

    # EXECUTION PHASE
    # = ENTRY POINT
    def execute(self, risk_params):
        log.info('Executing the calculation ...')
        results = self.run(risk_params)

        log.info('Finished calculation ...')

        return results

    # Preparation and presentation of results
    def results(self, result_data):
        # Sort for human beings first
        g = self.vnq_model.getGraph() # Load it from the model
        ordered_results = self.graphHelper.order_results(g, result_data)               # order the results to match human readability (nodes from 0 to n instead of arbitrary order)

        #Presentation of results
        vnq.VNQView.show_results(ordered_results) # console

        #Presentation of reports (warnings etc.)
        log.info("Analyzing reports ...")
        key_reports = reporting.ReportManager.keyReports()
        vnq.VNQView.displayStructuralFailures(key_reports)
        report_results = [r for r in reporting.ReportManager.reports.values()]
        vnq.VNQView.displayReports(report_results)


    # Computation method
    # TODO: Think about moving it to a model class
    # Risk_params: Eclectic risks need external calculation or estimation; give a list of 1s if you want to skip this computation step
    # entity_size: Pass market measurements only in the case the relationships are not on market scale (e.g. downscaled to a single service usage)
    #       Otherwise: Leave empty
    #       Manual input is always regarded to be symmetric (we do not distinguish whether an entity is a big supplier or customer, as the data typically does not exist. May be revised in the future.
    #       Order input by nodes
    def run(self, risk_params, entity_sizes):
        # Calculate basic bargaining powers
        # Does not include
        power_indicators = self.vnq_model.run(entity_sizes)

        # Presentation of final bargaining powers
        self.show_final_powers(power_indicators)

        #Make a ready to use weighted risk indicator
        rks_indicators = self.vnq_model.risks(risk_params)                                        # [3_RK]per entity

        #Bring both directions together and nosidepayments.py a single value
        result = self.vnq_model.vn_level(power_indicators, rks_indicators)                        # [3_FINAL] calc
        return result

    # Display the bargaining powers
    # -> Driving indicators
    def show_final_powers(self,power_indicators):
        # order to match human readability
        print power_indicators[0]
        g = self.vnq_model.getGraph() # load it from the model
        power_in = self.graphHelper.order_results(g, power_indicators[0])  # Incoming relationships (suppliers)
        power_out = self.graphHelper.order_results(g, power_indicators[1]) # Outgoing relationships (cusotmers)

        # Console presentation
        vnq.VNQView.displayFinalPowers(power_in, power_out)
        #displayFinalPowers(power_in, power_out)








