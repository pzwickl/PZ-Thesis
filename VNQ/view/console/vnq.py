import pprint

from numpy import argmax

from numpy import argmin
from numpy import average
from numpy import median

from app import params
from app.logger import log
from model import reporting


pp = pprint.PrettyPrinter(indent=4)    # advanced printing purposes

class VNQView:

    @staticmethod
    def welcome():
        print(params._VISUAL_MAIN_LINE_SEPARATOR)
        print(params._VISUAL_INLINE_MARKER + "Welcome to VNQ-App (Value Network Quantification Application)! \n\t Developed by P.Zwickl @ University of Vienna, Faculty of Computer Science, Cooperative Systems Group")
        print(params._VISUAL_NEW_LINE + params._VISUAL_INLINE_MARKER + "The application has been setup and may now be used and configured.")
        print(
            params._VISUAL_INLINE_MARKER + params._VISUAL_NOTE +
            "The usage of nodes without _in_ AND _out_ relationships (edges) may bias the computation and have to be removed (see reported warnings).")
        print(params._VISUAL_INLINE_MARKER + params._VISUAL_INLINE_MARKER + "yours, Patrick")
        print(params._VISUAL_MAIN_LINE_SEPARATOR)

        log.error('Computing ...')

    @staticmethod
    def show_results(results):

        # Start presenting results ...
        print params._VISUAL_LINE_SEPARATOR
        print params._VISUAL_INLINE_MARKER + 'Results ...'
        print params._VISUAL_LINE_SEPARATOR

        print params._VISUAL_INLINE_MARKER + 'All:'
        pp.pprint(results)

        max_index = argmax(results)
        min_index = argmin(results)
        print "\n" + params._VISUAL_INLINE_MARKER + 'Descriptive Statistics:'
        print 'Maximum Delta:' + params._VISUAL_INLINE_MARKER + str(results[max_index]) + params._VISUAL_INLINE_MARKER + params._VISUAL_INLINE_MARKER + '@ node ' + str(max_index) + ' (there could be multiple matches)'
        print 'Minimum Delta:' + params._VISUAL_INLINE_MARKER + str(results[min_index]) + params._VISUAL_INLINE_MARKER + params._VISUAL_INLINE_MARKER + '@ node ' + str(min_index) + ' (there could be multiple matches)'
        print 'Average Delta:' + params._VISUAL_INLINE_MARKER + str(average(results)) + params._VISUAL_INLINE_MARKER + params._VISUAL_INLINE_MARKER + '(preferable usage for small graphs)'
        print 'Median Delta:' + params._VISUAL_INLINE_MARKER + str(median(results)) + params._VISUAL_INLINE_MARKER + params._VISUAL_INLINE_MARKER + '(preferable usage for large graphs)'

        print params._VISUAL_LINE_SEPARATOR

#        print params._VISUAL_INLINE_MARKER + 'Main pitfalls (if any) ...'

#        reporting.ReportManager.analyzeReports()

        #print params._VISUAL_LINE_SEPARATOR

#        print params._VISUAL_INLINE_MARKER + 'All reports (if any) ...'

#        reporting.ReportManager.displayReports()

        # Show all end results plus min, max, etc.
#        print(params._VISUAL_MAIN_LINE_SEPARATOR)

#class ReportView(object):

    @staticmethod
    def displayPowerSize(ordered_powers, ordered_sizes):
        log.debug('Power: %s', ordered_powers)
        #log.debug(ordered_powers) # Print bargaining powers
        log.debug('Enity size: %s', ordered_sizes)
        #log.debug(ordered_sizes)  # Print entity sizes

    @staticmethod
    def displayFinalPowers(power_in, power_out):
        print 'Power indicators IN:'
        print(power_in)
        print 'Power indicators OUT:'
        print(power_out)


    @staticmethod
    def displayStructuralFailures(nodes):
        if(len(nodes) > 0):
            print params._VISUAL_INLINE_MARKER + 'Main structural issues:'
            for i in nodes:
                log.warning('Node ' + str(i.node) + ' seems disconnected from the VN (=graph). This corrupts the results.')
        else:
            print params._VISUAL_INLINE_MARKER + 'Structure validates successfully.'

    @staticmethod
    def displayReports(reports):
        #[r.display() for r in ReportManager.reports.values()]
        if len(reports) > 0:
            print params._VISUAL_INLINE_MARKER + 'Reports: ' + str(len(reports))
            print params._VISUAL_INLINE_MARKER + 'All reports:'
            [r.display() for r in reports] # TODO: Separate from logic here?
        else:
            print params._VISUAL_INLINE_MARKER + 'No reports recorded.'

