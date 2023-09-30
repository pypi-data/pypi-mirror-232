'''Tyke wrapper around OTel MySQLClient Instrumentor''' 
import logging
from opentelemetry.instrumentation.mysqlcleint import MySQLClientInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class MySQLClientInstrumentorWrapper(MySQLClientInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel MySQLClient Instrumentor class'''
