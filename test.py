#!/usr/bin/env python3
# coding=utf-8

"""
示例
"""

from oneforall import OneForAll

if __name__ == '__main__':
    test = OneForAll(target='hackfun.org')
    test.brute = True
    test.req = True
    test.takeover = True
    test.run()
    result = test.datas
