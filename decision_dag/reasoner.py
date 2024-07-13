#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from collections import OrderedDict
import time
import json
import logging

from gevent import monkey
from decision_dag.core.dag_builder import init_dag
from decision_dag.core.dag_executor import RunStatus, Engine

monkey.patch_all()

logging.getLogger().setLevel(logging.INFO)


def execute_process(process_id: str, params: list):
    # TODO get process definition, use local file for now
    project_root = os.path.basename(os.path.basename(__file__))
    file_path = os.path.join(project_root, f'knowledge_base/{process_id}.json')
    dag = json.load(open(file_path, encoding='utf8'))
    g = init_dag(dag)

    input_dict = {kv['name']: kv.get('value') for kv in params}
    data = OrderedDict(input_dict)

    serial_engine = Engine(1)

    # execute process
    before = time.time()
    error, status, data = serial_engine.eval(g, data, 600)
    take_time = time.time() - before

    _meta = {
        "start": before,
        "took": take_time,
        "engine": "serial_engine",
        "has_error": bool(error)
    }
    logging.info("gather all node output")
    all_result = {}
    for task in dag.get('dagTasks', []):
        node_id = task['id']
        node = g.get_node(node_id)
        node_result = {
            "_meta": {
                "took": node.took,  # 执行时间
                "has_error": node.state == 'error',  # 是否出错
                "error": node.error  # 错误信息
            }
        }
        if status[node_id] == RunStatus.FINISH:
            node_output = task.get('outputParams')
            for key, _ in node_output.items():
                node_result[key] = data.get(key)
            all_result[node_id] = node_result

    logging.info("gather graph output")
    result = {}
    output_params = dag.get('outputParams')
    for param_item in output_params:
        key = param_item['name']
        result[key] = data.get(key)

    return _meta, all_result, result
