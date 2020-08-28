""" Tablib - JSON Support
"""
import decimal
import json
from uuid import UUID

from . import tablib


def serialize_objects_handler(obj):
    if isinstance(obj, (decimal.Decimal, UUID)):
        return str(obj)
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return obj


class JSONFormat:
    title = 'json'
    extensions = ('json',)

    @classmethod
    def export_set(cls, dataset):
        """Returns JSON representation of Dataset."""
        return json.dumps(dataset.dict, default=serialize_objects_handler)

    @classmethod
    def export_book(cls, databook):
        """Returns JSON representation of Databook."""
        return json.dumps(databook._package(), default=serialize_objects_handler)

    @classmethod
    def import_set(cls, dset, in_stream):
        """Returns dataset from JSON stream."""

        dset.wipe()
        dset.dict = json.load(in_stream)

    @classmethod
    def import_book(cls, dbook, in_stream):
        """Returns databook from JSON stream."""

        dbook.wipe()
        for sheet in json.load(in_stream):
            data = tablib.Dataset()
            data.title = sheet['title']
            data.dict = sheet['data']
            dbook.add_sheet(data)

    @classmethod
    def detect(cls, stream):
        """Returns True if given stream is valid JSON."""
        try:
            json.load(stream)
            return True
        except (TypeError, ValueError):
            return False


""" Tablib - *SV Support.
"""

import csv
from io import StringIO


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

    @classmethod
    def import_set(cls, dset, in_stream, headers=True, **kwargs):
        """Returns dataset from CSV stream."""

        dset.wipe()

        kwargs.setdefault('delimiter', cls.DEFAULT_DELIMITER)

        rows = csv.reader(in_stream, **kwargs)
        for i, row in enumerate(rows):

            if (i == 0) and (headers):
                dset.headers = row
            elif row:
                if i > 0 and len(row) < dset.width:
                    row += [''] * (dset.width - len(row))
                dset.append(row)

    @classmethod
    def detect(cls, stream, delimiter=None):
        """Returns True if given stream is valid CSV."""
        try:
            csv.Sniffer().sniff(stream.read(1024), delimiters=delimiter or cls.DEFAULT_DELIMITER)
            return True
        except Exception:
            return False
