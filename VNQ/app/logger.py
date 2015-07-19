import logging
log = logging.getLogger('VNQ.log')

# All messages go to file handler
#fh = logging.FileHandler('vnq.log')
#fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# add the handlers to the logger
#log.addHandler(fh)
log.addHandler(ch)

#log.setLevel(logging.DEBUG)
##logger.setLevel(20)                 # 0 NOTSET, 10 DEBUG, 20 INFO, 30 WARNING, 40 ERROR, 50 CRITICAL