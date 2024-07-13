#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import time
from collections import OrderedDict
from enum import Enum

import gevent
from gevent.pool import Pool

from decision_dag.core.graph import Graph, Node


def func_wrap(node: Node, data):
    name = node.name
    tic = time.time()  # init time point
    logging.info('Node ' + name + ' start.')
    node.state = 'running'
    with gevent.Timeout(node.timeout, TimeoutError(name)):
        try:
            ret = node.op.func(name, data, node.conf)
            node.state = 'finish'
            if isinstance(ret, tuple):
                if not ret[0]:
                    node.state = 'error'
                    node.error = ret[1]
            else:
                if ret is not None:
                    node.state = 'error'
                    node.error = ret
        except Exception as e:
            node.state = 'error'
            node.error = "Internal Exception: " + str(e)
    toc = time.time()  # complete time point
    node.took = toc - tic
    # 抛出异常 以便流程捕获
    # 节点暂时不要抛出异常 由流程决定是否继续执行
    if node.state == "error":
        logging.error(f'{name} error:{node.error}')
    #     raise Exception(node.error)


class RunStatus(Enum):
    PENDING = 0
    START = 1
    FINISH = 2
    ERROR = -1


class Engine(object):
    def __init__(self, pool_size=100):
        self.p = Pool(pool_size)

    def submit(self, node: Node, data):
        job = self.p.spawn(func_wrap, node, data)
        job.name = node.name
        return job

    def eval(self, g: Graph, data=None, timeout=None):
        assert isinstance(g, Graph), 'g should be Graph instance.'
        assert g.frozen, 'Graph g should be frozen.'

        data = data or OrderedDict()
        run_status = {node: RunStatus.PENDING for node in g.nodes}
        process_error = {}

        ready = gevent.event.Event()
        ready.clear()

        def update(job):
            this_node = g.get_node(job.name)
            # 更新当前job状态
            run_status[job.name] = RunStatus.FINISH

            # 节点执行出错或到达结束节点 退出
            if not job.successful() or job.name == 'finish_node' or this_node.state == 'error':
                process_error["error"] = this_node.error
                process_error["error_node"] = job.name
                ready.set()
                return

            # 尝试提交子节点
            for out_node_name in g.out_nodes(job.name):
                if run_status[out_node_name] == RunStatus.PENDING:
                    # 判断父节点是否均完成
                    completed = True
                    for in_node_name in g.in_nodes(out_node_name):
                        if run_status[in_node_name] != RunStatus.FINISH:
                            completed = False
                            break
                    if completed:
                        next_job = self.submit(g.get_node(out_node_name), data)
                        next_job.link(update)
                        run_status[out_node_name] = RunStatus.START

        # 从start节点开始执行
        run_status['start_node'] = RunStatus.START
        try:
            start_job = self.submit(g.get_node('start_node'), data)
            start_job.link(update)
            ready.wait(timeout=timeout)
        except Exception as e:
            process_error["error"] = "Process Exception: " + str(e)
            logging.error(str(e))
        return process_error.get("error"), run_status, data


if __name__ == '__main__':
    from decision_dag.core.graph import Node, Op

    tic = time.time()
    g = Graph()
    sleep_3_op = Op('sleep_3_op', lambda x, y, z: logging.info(
        'Sleep 3s. ' + str(time.sleep(3))))
    sleep_5_op = Op('sleep_5_op', lambda x, y, z: logging.info(
        'Sleep 5s. ' + str(time.sleep(5))))
    sleep_node_a = Node('sleep_node_a', sleep_5_op)
    sleep_node_b = Node('sleep_node_b', sleep_3_op, timeout=2.5)
    sleep_node_c = Node('sleep_node_c', sleep_3_op)
    g.add_nodes_from([sleep_node_a, sleep_node_b, sleep_node_c])
    g.add_edges_from([(sleep_node_b.name, sleep_node_c.name)])
    g.froze()
    print('build graph time: %s' % str(time.time() - tic))

    tic = time.time()
    engine = Engine()
    print('build engine time: %s' % str(time.time() - tic))

    tic = time.time()
    print(engine.eval(g))
    print('run graph time: %s' % str(time.time() - tic))
