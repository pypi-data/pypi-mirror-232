'''Tyke wrapper around OTel Cassandra and Scylla Instrumentor''' 
import logging
from opentelemetry.instrumentation.cassandra import CassandraInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point
class CassandraInstrumentorWrapper(CassandraInstrumentor, BaseInstrumentorWrapper):
    '''Tyke wrapper around OTel Cassandra Instrumentor class'''
