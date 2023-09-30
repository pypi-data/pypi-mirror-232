'''Tyke wrapper around OTel PyMongo Instrumentor''' 
import logging
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from tyke.agent.instrumentation import BaseInstrumentorWrapper
from opentelemetry.trace.span import Span
from pymongo import monitoring

# Initialize logger with local module name
_logger = logging.getLogger(__name__)

# # The main entry point
# class PymongoInstrumentorWrapper(PymongoInstrumentor, BaseInstrumentorWrapper):
#     '''Tyke wrapper around OTel PyMongo Instrumentor class'''

class PymongoInstrumentorWrapper(BaseInstrumentorWrapper):
    def instrument(self):
        """configure django instrumentor w hooks"""
        PymongoInstrumentor().instrument(request_hook=self.request_hook)

    '''Tyke wrapper around OTel PyMongo Instrumentor class'''
    def request_hook(self, span: Span, event: monitoring.CommandStartedEvent):
        try:
            command = event.command.get(event.command_name, "")
            span.set_attribute("db.sql.table", command)
        except Exception as err:  # pylint:disable=W0703
            return 