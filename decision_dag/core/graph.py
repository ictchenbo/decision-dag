#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict

import networkx as nx

from decision_dag.core.op_manager import Op, finish_op, start_op


class Node(object):
    def __init__(self, name: str, op: Op, conf=None, timeout=None):
        assert isinstance(op, Op), 'Input op is not Op class.'
        self.name = name
        self.op = op
        self.conf = conf
        self.timeout = timeout
        self.state = 'init'
        self.took = None
        self.error = None


start_node = Node('start_node', start_op)
finish_node = Node('finish_node', finish_op)


def get_start_nodes(nodes, edges, idx=0):
    starts = {node for node in nodes}
    for edge in edges:
        node = edge[idx]
        if node in starts:
            starts.remove(node)
    return list(starts)


class Graph(object):
    def __init__(self, name='default'):
        self.g = nx.DiGraph(name=name)
        self.tr = None
        self.node_collection = OrderedDict()
        self.edge_collection = OrderedDict()
        self._frozen = False

    # 添加node
    def add_node(self, node: Node):
        assert self._frozen is False, 'Graph has frozen, when add node.'
        assert isinstance(node, Node), 'Input node is not Node class.'
        self.g.add_node(node.name)
        self.node_collection[node.name] = node
        return node.name

    def add_nodes_from(self, nodes):
        for node in nodes:
            self.add_node(node)

    # 添加edge
    def add_edge(self, node_a, node_b):
        assert self._frozen is False, 'Graph has frozen, when add edge.'
        edge_name = f'{node_a}__{node_b}'
        if edge_name not in self.edge_collection:
            self.g.add_edge(node_a, node_b)
            self.edge_collection[edge_name] = (node_a, node_b)
        return edge_name

    def add_edges_from(self, edges):
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    # 全部父节点
    def ancestors(self, node_name):
        if self._frozen:
            return nx.ancestors(self.tr, node_name)
        else:
            return nx.ancestors(self.g, node_name)

    # 相邻父节点
    def in_nodes(self, node_name):
        if self._frozen:
            in_edges = self.tr.in_edges(node_name)
        else:
            in_edges = self.g.in_edges(node_name)
        return [edge[0] for edge in in_edges]

    # 相邻子节点
    def out_nodes(self, node_name):
        if self._frozen:
            out_edges = self.tr.out_edges(node_name)
        else:
            out_edges = self.g.out_edges(node_name)
        return [edge[1] for edge in out_edges]

    # 获取node对象
    def get_node(self, node_name) -> Node:
        node = self.node_collection.get(node_name)
        assert node is not None, 'Get None with node name: %s.' % node_name
        return node

    # 是否dag
    def is_dag(self):
        return nx.is_directed_acyclic_graph(self.g)

    # 冻结graph
    def froze(self, starts=None, ends=None):
        # nx.topological_generations(self.g)
        nodes = [n for n in self.nodes]
        edges = [e for e in self.edges]
        self.add_node(start_node)
        self.add_node(finish_node)

        for start in starts or get_start_nodes(nodes, edges, 1):
            self.add_edge(start_node.name, start)

        for end in ends or get_start_nodes(nodes, edges):
            self.add_edge(end, finish_node.name)

        assert self.is_dag(), 'Graph is not a dag.'
        self.tr = nx.transitive_reduction(self.g)
        self._frozen = True

        print(self.node_collection)

    @property
    def frozen(self):
        return self._frozen

    @property
    def nodes(self):
        return self.g.nodes

    @property
    def edges(self):
        return self.g.edges


if __name__ == '__main__':
    import logging
    import time

    g = Graph()
    print(id(g))
    print(g)
    print(g.__dict__)

    sleep_3_op = Op('sleep_3_op', lambda x, y, z: logging.info(
        'Sleep 3s. ' + str(time.sleep(3))))
    sleep_5_op = Op('sleep_5_op', lambda x, y, z: logging.info(
        'Sleep 5s. ' + str(time.sleep(5))))
    sleep_node_a = Node('sleep_node_a', sleep_5_op)
    sleep_node_b = Node('sleep_node_b', sleep_3_op)
    sleep_node_c = Node('sleep_node_c', sleep_3_op)
    g.add_nodes_from([sleep_node_a, sleep_node_b, sleep_node_c])
    g.add_edges_from([(sleep_node_b.name, sleep_node_c.name)])
    g.froze()
    print(g.frozen)

    print(g.nodes)
    print(g.edges)
    print(g.tr.nodes)
    print(g.tr.edges)

    for node_name in g.nodes:
        print(g.get_node(node_name).__dict__)

    print(id(g))
    print(g)
    print(g.__dict__)

    print(g.ancestors('finish_node'))
    print(g.in_nodes('finish_node'))
    print(g.out_nodes('start_node'))
