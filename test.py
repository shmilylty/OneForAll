#!/usr/bin/env python3
# coding=utf-8

"""
Example
"""

from oneforall import OneForAll


def oneforall(domain):
    test = OneForAll(target=domain)
    test.brute = True
    test.req = True
    test.takeover = True
    test.run()


if __name__ == '__main__':
    oneforall('freebuf.com')
