""" Tablib - formats
"""
from collections import OrderedDict
from .format import JSONFormat, CSVFormat


class Registry(object):
    _formats = OrderedDict()

    def register(self, key, format_or_path):
        # Create Databook.<format> read or read/write properties

        # Create Dataset.<format> read or read/write properties,
        # and Dataset.get_<format>/set_<format> methods.
        self._formats[key] = format_or_path

    def register_builtins(self):
        # Registration ordering matters for autodetection.
        self.register('csv', CSVFormat())
        self.register('json', JSONFormat())

    def get_format(self, key):
        if key not in self._formats:
            raise Exception("OneForAll has no format '%s'." % key)
        return self._formats[key]


registry = Registry()
