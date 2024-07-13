from functools import partial

from decision_dag.core.graph import Graph, Node
from decision_dag.core.op_manager import Op
from decision_dag.core.service_proxy import service_op, script_op, external_script_op


def choose_service(task_type):
    return {
        "service": service_op,
        "script": script_op,
        "external_script": external_script_op
    }[task_type]


def init_dag(dag_conf: dict) -> Graph:
    g = Graph(f'{dag_conf.get("name")}[{dag_conf.get("id")}]')
    # op_manager = OpManager()
    tasks = dag_conf['dagTasks']
    for task in tasks:
        task_id = task['id']
        task_op = Op(
                task_id,
                partial(
                    choose_service(task.get("type", "service")),
                    input_params=task.get('inputParams'),
                    output_params=task['outputParams']
                )
            )
        # op_manager.add(task_op)
        g.add_node(Node(task_id, task_op, task))

    deps = dag_conf.get('taskDependencies')
    if not deps:
        deps = []
        for i in range(1, len(tasks)):
            deps.append((tasks[i-1]["id"], tasks[i]["id"]))

    g.add_edges_from(deps)
    g.froze()
    return g
