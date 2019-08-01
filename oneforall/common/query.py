# coding=utf-8
from .module import Module


class Query(Module):
    """
    查询基类
    """
    def __init__(self):
        Module.__init__(self)
