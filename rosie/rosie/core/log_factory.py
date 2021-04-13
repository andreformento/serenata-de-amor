import logging
import os

class LogFactory():
    LOG_LEVEL = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO').upper())

    def __init__(self, class_name):
        self.class_name = class_name
        logging.basicConfig(level=self.LOG_LEVEL)

    def create(self):
        log = logging.getLogger(self.class_name)
        log.setLevel(self.LOG_LEVEL)
        return log
