from flask import Flask, request

from decision_dag.reasoner import execute_process

from decision_dag.engine.rule_engine import RuleEngine
from decision_dag.engine.timespace_engine import space_relation, time_relation
from decision_dag.engine.path_engine import get_path_points

app = Flask(__name__)
# logging.getLogger().setLevel(logging.DEBUG)


@app.route('/inference/_execute/timespace', methods=['GET', 'POST'])
def timespace_reason():
    """
    时空推理服务 对输入两个实体 分别获取其时间信息和空间信息 进而计算时间和空间关系
    :return:
    """
    from mock_service import get_entity_detail, get_xy, get_time

    params = request.args
    head_id = params.get('startId')
    tail_id = params.get('tailId')
    if not head_id or not tail_id:
        return {
            "code": 40000,
            "msg": "参数无效 需要startId和tailId"
        }, 400

    # 1. 查询实体基础信息，类型、时间信息、空间信息
    try:
        ok1, head_entity = get_entity_detail(head_id)
        ok2, tail_entity = get_entity_detail(tail_id)
    except Exception as e:
        return {
            "code": 50000,
            "msg": str(e)
        }, 500

    if not ok1 or not ok2:
        return {
            "code": 40400,
            "msg": "实体未找到! id不正确?"
        }, 404

    ret_data = {}
    # 2. 如果都包含空间信息，基于坐标计算空间关系
    sx, sy = get_xy(head_entity), get_xy(tail_entity)
    if sx and sy:
        ret_data["space"] = space_relation(sx, sy)
    # 3. 如果都包含时间信息，计算时间关系
    tx, ty = get_time(head_entity), get_time(tail_entity)
    if tx and ty:
        tr = time_relation(tx, ty)
        if isinstance(tr, tuple):
            rs = "早" if tr[0] == "Before" else "晚"
            tdiff = f'{tr[1]/3600:0.1f}小时' if tr[1] > 3600 else f'{tr[1]/60:0.1f}分钟'
            ret_data["time"] = rs + tdiff
        else:
            ret_data["time"] = tr

    relations = []
    if "space" in ret_data:
        relation = ret_data["space"]["direction"]
        relations.append({
            "headId": head_id,
            "relationId": f"R_SPACE_{head_id}_{tail_id}",
            "relationName": relation,
            "type": "SPACE",
            "tailId": tail_id,
            "isNew": True,
            "confidence": 100.0,
            "space": ret_data["space"]
        })
    if "time" in ret_data:
        relation = ret_data["time"]
        relations.append({
            "headId": head_id,
            "relationId": f"R_TIME_{head_id}_{tail_id}",
            "relationName": relation,
            "type": "TIME",
            "tailId": tail_id,
            "isNew": True,
            "confidence": 100.0
        })

    ret_data["relations"] = relations

    return {
        "code": 20000,
        "msg": "OK",
        "data": ret_data
    }


@app.route('/inference/_execute/rules', methods=['POST'])
def rule_engine():
    """
    规则判决服务，输入事实集，基于指定的规则集构建规则引擎，返回判决结果
    :return:
    """
    params = request.json
    env_object = params.get('env_object')
    facts = params.get('facts')
    if isinstance(facts, dict):
        facts = [facts]

    engine = RuleEngine(params.get('rule_id'))
    engine.add_facts(env_object, facts)
    engine.build()

    subject = params.get('subject')
    query = params.get('query')
    datalog_query = f'{query}("{subject}", "{env_object}")'
    result = engine.ask(datalog_query)

    return {
        "code": 20000,
        "msg": "OK",
        "data": {
            "query": datalog_query,
            "result": "是" if result else "否"
        }
    }


@app.route('/inference/_execute/dags', methods=['GET', 'POST'])
def dags_server():
    """
    决策推理服务 基于提供的流程输入参数，执行指定的流程，返回流程执行结果
    :return:
    """
    params = request.json

    process_params = params.get('params', [])
    process_id = params.get('processId') or 'dag_error'

    meta, all_result, output = execute_process(process_id, process_params)

    if isinstance(meta, str):
        return {
            "code": all_result,
            "msg": meta
        }, int(all_result/100)

    return {
        "code": 20000,
        "msg": "OK",
        "data": {
            "processId": process_id,
            "procecssExecutionId": "100001",
            "_meta": meta,
            "resultInfo": all_result,
            "outputParams": [output]
        }
    }


@app.route('/inference/_execute/rules_speed', methods=['GET', 'POST'])
def rule_engine_2():
    """
    速度判决规则服务，基于指定的计算规则、指定的时间、活动主题，计算主体通信速度
    :return:
    """
    from mock_service import get_env

    params = request.args
    rule_id = params.get("rule_id", "speed")
    time = params.get("time")
    print(time)
    info = get_env(time)
    if info is None:
        return {
            "code": 40400,
            "msg": "没有相关环境信息"
        }, 404
    facts = [info]

    env_subject = params.get('env_subject', '环境1')

    engine = RuleEngine(rule_id)
    engine.add_facts(env_subject, facts)
    engine.build()

    subject = params.get('subject', '人员1')
    query = params.get('query', '速度')
    datalog_query = f'{query}["{env_subject}","{subject}"] == Z'
    result = engine.ask(datalog_query)

    return {
        "code": 20000,
        "msg": "OK",
        "data": {
            "query": datalog_query,
            "result": result[0][0] if result else None
        }
    }


@app.route('/inference/_execute/path_points', methods=['GET', 'POST'])
def infer_path_points():
    """
    根据提供的路线 获取环境信息 基于规则进行速度计算 从而模拟出路线的时间流程
    :return:
    """
    from mock_service import get_navigate_path

    params = request.args
    start = params.get("start")
    end = params.get("end")
    time = params.get("time")
    paths = get_navigate_path(start, end)
    ret_data = {}
    for key, path in paths.items():
        path_info = get_path_points(path, time)
        ret_data[key] = path_info
    return {
        "code": 20000,
        "data": {
            "data": ret_data
        }
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8282, debug=True)
