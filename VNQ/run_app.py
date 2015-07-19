from app import params
from controller import vnqcontroller

__author__ = 'patrick'

#if __name__ == '__main__':
    #APPLICATION CODE
print 'Start test run...'
v = vnqcontroller.VNQController()  # instantiate with empty graph
#print(v.g)
v.configure(params._SAMPLE_JSON_FILE)  # load specified graph
v.execute([1, 1, 1, 1, 1])