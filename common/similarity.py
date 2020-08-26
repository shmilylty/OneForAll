"""
根据网页结构判断页面相似性(Determine page similarity based on HTML page structure)
判断方法：根据网页的DOM树确定网页的模板特征向量，对模板特征向量计算网页结构相似性。
来源地址：https://github.com/SPuerBRead/HTMLSimilarity
计算参考: https://patents.google.com/patent/CN101694668B/zh
"""
from treelib import Tree
from bs4 import BeautifulSoup
import bs4


class DOMTree(object):
    def __init__(self, label, attrs):
        self.label = label
        self.attrs = attrs


class HTMLParser(object):
    def __init__(self, html):
        self.dom_id = 1
        self.dom_tree = Tree()
        self.bs_html = BeautifulSoup(html, 'html.parser')

    def get_dom_structure_tree(self):
        for content in self.bs_html.contents:
            if isinstance(content, bs4.element.Tag):
                self.bs_html = content
        self.recursive_descendants(self.bs_html, 1)
        return self.dom_tree

    def recursive_descendants(self, descendants, parent_id):
        if self.dom_id == 1:
            self.dom_tree.create_node(descendants.name, self.dom_id,
                                      data=DOMTree(descendants.name, descendants.attrs))
            self.dom_id = self.dom_id + 1
        for child in descendants.contents:
            if isinstance(child, bs4.element.Tag):
                self.dom_tree.create_node(child.name, self.dom_id, parent_id,
                                          data=DOMTree(child.name, child.attrs))
                self.dom_id = self.dom_id + 1
                self.recursive_descendants(child, self.dom_id - 1)


class Converter(object):
    def __init__(self, dom_tree, dimension):
        self.dom_tree = dom_tree
        self.node_info_list = []
        self.dimension = dimension
        self.initial_weight = 1
        self.attenuation_ratio = 0.6
        self.dom_eigenvector = {}.fromkeys(range(0, dimension), 0)

    def get_eigenvector(self):
        for node_id in range(1, self.dom_tree.size() + 1):
            node = self.dom_tree.get_node(node_id)
            node_feature = self.create_feature(node)
            feature_hash = self.feature_hash(node_feature)
            node_weight = self.calculate_weight(node, node_id, feature_hash)
            self.construct_eigenvector(feature_hash, node_weight)
        return self.dom_eigenvector

    @staticmethod
    def create_feature(node):
        node_attr_list = []
        node_feature = node.data.label + '|'
        for attr in node.data.attrs.keys():
            node_attr_list.append(attr + ':' + str(node.data.attrs[attr]))
        node_feature += '|'.join(node_attr_list)
        return node_feature

    @staticmethod
    def feature_hash(node_feature):
        return abs(hash(node_feature)) % (10 ** 8)

    def calculate_weight(self, node, node_id, feature_hash):
        brother_node_count = 0
        depth = self.dom_tree.depth(node)
        for brother_node in self.dom_tree.siblings(node_id):
            brother_node_feature = self.create_feature(brother_node)
            brother_node_feature_hash = self.feature_hash(brother_node_feature)
            if brother_node_feature_hash == feature_hash:
                brother_node_count = brother_node_count + 1
        if brother_node_count:
            node_weight = self.initial_weight * self.attenuation_ratio ** depth \
                          * self.attenuation_ratio ** brother_node_count
        else:
            node_weight = self.initial_weight * self.attenuation_ratio ** depth
        return node_weight

    def construct_eigenvector(self, feature_hash, node_weight):
        feature_hash = feature_hash % self.dimension
        self.dom_eigenvector[feature_hash] += node_weight


def calc_pseudodistance(dom1_eigenvector, dom2_eigenvector, dimension):
    a, b = 0, 0
    for i in range(dimension):
        a += dom1_eigenvector[i]-dom2_eigenvector[i]
        if dom1_eigenvector[i] and dom2_eigenvector[i]:
            b += dom1_eigenvector[i] + dom2_eigenvector[i]
    pseudodistance = abs(a)/b
    return pseudodistance


def get_pseudodistance(html_doc1, html_doc2, dimension=5000):
    """
    获取html文档结构相似度

    :param str html_doc1: html文档
    :param str html_doc2: html文档
    :param int dimension: 降维后的维数
    :return 伪距离
    """
    hp1 = HTMLParser(html_doc1)
    html_doc1_dom_tree = hp1.get_dom_structure_tree()
    hp2 = HTMLParser(html_doc2)
    html_doc2_dom_tree = hp2.get_dom_structure_tree()
    converter = Converter(html_doc1_dom_tree, dimension)
    dom1_eigenvector = converter.get_eigenvector()
    converter = Converter(html_doc2_dom_tree, dimension)
    dom2_eigenvector = converter.get_eigenvector()
    return calc_pseudodistance(dom1_eigenvector, dom2_eigenvector, dimension)


def is_similar(html_doc1, html_doc2, dimension=5000):
    """
    根据计算出的伪距离来判断是否html页面结构相似

    :param str html_doc1: html文档
    :param str html_doc2: html文档
    :param int dimension: 降维后的维数
    :return 是否相似（伪距离value<0.2时相似，value>0.2时不相似）
    """
    value = get_pseudodistance(html_doc1, html_doc2, dimension)
    if value > 0.2:
        return False
    else:
        return True
