import logging

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
logPath = "logs"
fileName = "test"
fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
logging.getLogger().setLevel(logging.DEBUG)
logging.info('Useful message')
logging.error('Something bad happened')
print("test message")

# log_file = get_date_string(datetime.now())+'_gitlab_collecter.log'
# # instantiate a logger object 
# logging.basicConfig(
#   format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
#   datefmt='%Y-%m-%d:%H:%M:%S',
#   level=logging.DEBUG,
#   filename='logs/'+log_file
# )