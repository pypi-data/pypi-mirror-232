import logging

def setup_logger(logfile="my_log.log"):
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)
