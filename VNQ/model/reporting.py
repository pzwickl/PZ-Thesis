#This module serves the purpose of reporting exceptional things or producing statistics (if required)

from abc import abstractmethod


# What is a report?
# A report is a -> lazy <- form of error detection.
# Rather than raising an error the problem is filed as report and given to further analysis by the user,
# if the computation can be continued
# REASON: Error handling during computation would require traversing the graph one more time (due to VNQ computation process).
# This is inefficient.
# WARNING: Reports may indicate whether results are applicable or not.
# USAGE: Instantiate and then register with the ReportManger which may then be called
from app import params


class Report(object):
    @abstractmethod
    def display(self):
        pass

class NoEdgeReport(Report):

    def __init__(self, node, type):
        self.node = node
        self.type = type

    def display(self):
        print params._VISUAL_LIST_SIGN + '[NoEdge] ' + params._VISUAL_INLINE_MARKER + 'Node' + str(self.node) + ': No relationship (=edge) of type \'' + str(self.type) + '\''

class InputReport(Report):
    def __init__(self, message):
        self.message = message
        #self.issued = 0                        #has it already been shown to the user

    def display(self):
        #if self.issued is 0:
        print params._VISUAL_LIST_SIGN + '[Input]' + params._VISUAL_INLINE_MARKER + self.message
        #    self.issued = 1                    #don't repeat (it is a generic warning, not a warning to be shown at each run)


class ReportManager(object):

    #reports = [] #static
    reports = {}    #static; is now dictionary in order to avoid double reports

    @staticmethod
    def registerReport(key, report=Report):
        if report is None:
            raise TypeError('A report cannot be none. None disrupts the displaying.')
        ReportManager.reports[key] = report
        #ReportManager.reports.append(report)

    @staticmethod
    def keyReports():
        results = ReportManager.analyzeDisconnection()
        return results
        #HELPERS

    @staticmethod
    def analyzeDisconnection():
        #Find nodes that have reports for incoming and outcoming relationships
        #Give a warning
        ignore = []         # do not report twice

        #errorCount = 0
        node_list = []
        for i in [i for i in ReportManager.reports.values() if isinstance(i, NoEdgeReport)]:
            ignore.append(i)
            correlated_errors = [j.display for j in ReportManager.reports.values() if isinstance(j, NoEdgeReport) and i.node is j.node and not (j in ignore) and not (i.type is j.type)]
            if len(correlated_errors) > 0:
                node_list.append(str(i.node));
                #print params._VISUAL_ERROR + 'Node ' + str(i.node) + ' seems disconnected from the VN (=graph). This corrupts the results.'
                ignore.extend(correlated_errors)
                #errorCount += 1
        #print params._VISUAL_INLINE_MARKER + 'Reports: ' + str(errorCount)
        return node_list


