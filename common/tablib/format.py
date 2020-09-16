import decimal
import json
import csv
from io import StringIO
from uuid import UUID

""" Tablib - formats
"""
from collections import OrderedDict


class Registry:
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


def serialize_objects_handler(obj):
    if isinstance(obj, (decimal.Decimal, UUID)):
        return str(obj)
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return obj


"""
Tablib - JSON Support
"""


class JSONFormat:
    title = 'json'
    extensions = ('json',)

    @classmethod
    def export_set(cls, dataset):
        """Returns JSON representation of Dataset."""
        return json.dumps(dataset.dict, default=serialize_objects_handler)


""" Tablib - CSV Support.
"""


class CSVFormat:
    title = 'csv'
    extensions = ('csv',)

    DEFAULT_DELIMITER = ','

    @classmethod
    def export_stream_set(cls, dataset, **kwargs):
        """Returns CSV representation of Dataset as file-like."""
        stream = StringIO()

        kwargs.setdefault('delimiter', cls.DEFAULT_DELIMITER)

        _csv = csv.writer(stream, **kwargs)

        for row in dataset._package(dicts=False):
            _csv.writerow(row)

        stream.seek(0)
        return stream

    @classmethod
    def export_set(cls, dataset, **kwargs):
        """Returns CSV representation of Dataset."""
        stream = cls.export_stream_set(dataset, **kwargs)
        return stream.getvalue()
