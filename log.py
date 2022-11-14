import logging
logging.basicConfig(filename='myfirstlog.log', level=logging.DEBUG, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logging.basicConfig(level=logging.INFO)
logging.info('I\'m an informational message.')
logging.debug('I\'m a message for debugging purposes.')
logging.warning('I\'m a warning. Beware!')
logging.error('This is error.')
logging.critical('This is critical.')
