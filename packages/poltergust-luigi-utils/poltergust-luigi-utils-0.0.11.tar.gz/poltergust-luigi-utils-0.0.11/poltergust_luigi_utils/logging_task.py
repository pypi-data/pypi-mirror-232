import os.path
import yaml
import sys
import traceback
import luigi
import luigi.contrib.gcs
import luigi.format
import luigi.mock
import luigi.local_target
import traceback
import math
import time
import datetime
import contextlib
import json
from . import caching
import logging
import shutil
import io
import yaml


class YamlFormatter(logging.Formatter):
    def __init__(self, include=False, **kw):
        logging.Formatter.__init__(self)
        self.include = include
        self.kw = kw
        
    def format(self, record):
        d = dict(self.kw)
        d.update(record.__dict__)
        d["time"] = self.formatTime(record)
        if self.include is not True:
            d = {k:v for k, v in d.items() if k in self.include}
        return yaml.safe_dump([d])

class LoggingTask(object):
    @classmethod
    def logging_progress_percentage(cls, x, a=0.5):
        return 100 * a * math.log(1 + x) / (1 + a*math.log(1 + x))

    logging_count = 0

    logging_formatter_yaml = False
    logging_formatter_yaml_include = ["time", "extra", "task", "msg"]

    def get_logging_formatter(self):
        if self.logging_formatter_yaml:
            return YamlFormatter(task=str(self), include=self.logging_formatter_yaml_include)
        else:
            return logging.Formatter(
                fmt="%(asctime)s " +  str(self) + ": %(message)s")
    
    @contextlib.contextmanager
    def logging(self, rethrow_errors=True):
        self.logging_stringio = io.StringIO()
        try:

            t = type(self)
            name = "%s.%s" % (t.__module__, t.__name__)
            self.logging_handler = logging.StreamHandler(self.logging_stringio)
            self.logging_formatter = self.get_logging_formatter()
            self.logging_handler.setFormatter(self.logging_formatter)
            self.logging_logger = logging.Logger(name)
            self.logging_logger.addHandler(self.logging_handler)

            try:
                yield self.logging_logger
            except Exception as e:
                self.logging_logger.exception("Runtime error")
                if rethrow_errors:
                    raise
            else:
                 self.logging_logger.info("DONE")

        finally:
            with self.logfile().open("w") as f:
                self.logging_stringio.seek(0)
                shutil.copyfileobj(self.logging_stringio, f)
                 
    def log(self, msg, *args, **kwargs):
        self.logging_count += 1
        self.logging_logger.info(msg, *args, **kwargs)
        self.set_status_message(self.logging_stringio.getvalue())
        if self.logging_progress_percentage is not None:
            self.set_progress_percentage(self.logging_progress_percentage(self.logging_count))
            
class TestLoggingTask(LoggingTask):
    logging_formatter_yaml = True

    def logfile(self):
        return caching.CachingOpenerTarget("file://" + os.getcwd() + "/test.log")

    def set_status_message(self, msg):
        pass
    
    def set_progress_percentage(self, pcnt):
        pass
    
