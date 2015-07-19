# ALL PARAMETERS ARE COLLECTED HERE
import os

__author__ = 'patrick zwickl'

_VALUES = 'PARAM'
_BEST = 'best'
_WITHIN_RELATIONSHIP_V = 2  #Being used for comparing the instances of a relationship (overweighting necessary)
_WITHIN_ENTITY_V = 2  #Std. V being used for comparing the best alternatives of each relationship of an entity

_WR = 0.33333   #Weighting factor R for delta_r (dr) ... risks
_W1 = 0.33333   #Weighting factor R for delta_1
_W2 = 0.33333   #Weighting factor R for delta_2

#REPORTING PARAMETERS
_NO_RELATIONSHIP_INEQUALITY = 1     # This is the inequality when not a single relationship exists (please, remove nodes where this applies for both in and out relationships)
_ONLY_ONE_RELATIONSHIP_INEQUALITY = 1

#VISUAL PARAMETERS
_VISUAL_INLINE_MARKER = '\t'    # When printing things used to highlight the line
_VISUAL_NEW_LINE = '\n'         # New line
_VISUAL_LIST_SIGN = '- '        # When listing e.g. results or reports
_VISUAL_MAIN_LINE_SEPARATOR = '========================================================================================='
_VISUAL_LINE_SEPARATOR = '-----------------------------------------------------------------------------------------'
_VISUAL_NOTE = '[NOTE] '
_VISUAL_WARNING = '[WARNING] '
_VISUAL_ERROR = '[ERROR]! '

#FILES

_PATH = os.path.dirname(os.path.realpath(__file__))
_TEST_FOLDER = "/Test/"

#print(_PATH+_TEST_FOLDER+"test.json")

_SAMPLE_JSON_FILE = _PATH+_TEST_FOLDER+"test.json"
_SAMPLE_BIT_FILE = _PATH+_TEST_FOLDER+"test.bitstram"
_UNIT_TEST_FILE = _PATH+_TEST_FOLDER+"testcase.json"
_UNIT_TEST_FILE_STATIC = _PATH+_TEST_FOLDER + "testcase_static.json"

#_SAMPLE_JSON_FILE = '/Users/patrick/OfficeCb/workspace/VNQAPP/Test/test.json'
#_SAMPLE_BIT_FILE = '/Users/patrick/OfficeCb/workspace/VNQAPP/Test/test.bitstram'
#_UNIT_TEST_FILE = '/Users/patrick/OfficeCb/workspace/VNQAPP/Test/testcase.json'
#_UNIT_TEST_FILE_STATIC = '/Users/patrick/OfficeCb/workspace/VNQAPP/Test/testcase_static.json'