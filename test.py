#!/usr/bin/env python3
# coding=utf-8

"""
Example
"""

from oneforall import OneForAll
from dbexport import export


def oneforall(target):
    test = OneForAll(target=target)
    test.brute = True
    test.req = True
    test.takeover = True
    test.run()


if __name__ == '__main__':
    TARGET = 'freebuf.com'
    oneforall(target=TARGET)
    export(target=TARGET)
