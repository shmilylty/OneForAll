#!/usr/bin/env python3
# coding=utf-8

"""
示例
"""

import oneforall

if __name__ == '__main__':
    test = oneforall.OneForAll(target='freebuf.com')
    test.brute = False
    test.takeover = True
    test.run()
    result = test.datas
