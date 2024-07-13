import logging
import requests
import json
import os
from mock_service import get_entity_detail

project_base = os.path.basename(os.path.basename(os.path.basename(__file__)))
file_path = os.path.join(project_base, 'service_config.json')
service_config = json.load(open(file_path))


def match_service(spec: str):
    name = spec
    version = None
    if '/' in spec:
        ss = spec.split('/')
        name = ss[0]
        version = ss[1]
    for service in service_config:
        if service['name'] == name and (version is None or version == service['version']):
            return service
    return None


def extract_value(data, vkey):
    if isinstance(vkey, str) and vkey.startswith('@'):
        return data[vkey[1:]]
    if isinstance(vkey, dict):
        return {k: extract_value(data, v) for k, v in vkey.items()}
    if isinstance(vkey, list):
        return [extract_value(data, vi) for vi in vkey]
    return vkey


def output_data(res_data, output_data, output_params):
    for key, value in output_params.items():
        output_data[key] = extract_value(res_data, value)


def service_op(name, data, conf, input_params, output_params):
    """
    调用外部服务
    :param name:
    :param data:
    :param conf:
    :param input_params:
    :param output_params:
    :return:
    """
    logging.info(f"http_op: {name}")
    service_spec = conf["service"]
    service = match_service(service_spec)
    if service is None:
        logging.error(f"service {service_spec} not found!")
        return False, "mismatch service! bad configuration?"
    payload = {}
    for key, value in input_params.items():
        payload[key] = extract_value(data, value)

    # TODO 不同服务定义的请求方式和参数不一，两种方案：（1）针对不同服务 提供不同实现  （2）采用jsonpath设置参数和提取返回值

    # if service_spec.startswith("基础知识服务"):
    #     ok, res_data = get_basic_entity(service, payload, data)
    #     if ok and res_data:
    #         output_data(res_data, data, output_params)
    #         return True, None

    method = service.get('method', 'POST')
    api_address = service.get('api_address')
    if method == 'GET':
        res = requests.get(api_address, params=payload)
    else:
        res = requests.request(method, api_address, json=payload)
    if res.status_code == 200:
        res_data = res.json()
        if "data" in res_data and "code" in res_data:
            res_data = res_data["data"]
        output_data(res_data, data, output_params)
        return True, None
    else:
        return False, res.text


def script_op(name: str, data, conf: dict = None, input_params: dict = None, output_params: dict = None, script: str = None):
    """
    执行本地脚本（表达式）
    :param name:
    :param data:
    :param conf:
    :param input_params:
    :param output_params:
    :return:
    """
    script = script or conf.get('script')
    if script is None:
        return False, "script empty!"
    env = locals()
    # 可以访问当前上下文数据
    env.update(data)

    global_env = {}

    # 添加额外数据
    if input_params:
        for key, value in input_params.items():
            if key == '_imports' and isinstance(value, list):
                for vi in value:
                    global_env[vi] == __import__(vi)
            env[key] = extract_value(data, value)
    # 执行脚本
    try:
        res = exec(script, global_env, env)
    except Exception as e:
        return False, str(e)
    # 输出
    output_data(env, data, output_params)

    return True, None


def external_script_op(name, data, conf, input_params, output_params):
    """
    执行外部脚本文件
    :param name:
    :param data:
    :param conf:
    :param input_params:
    :param output_params:
    :return:
    """
    script = conf['external_script']
    script = os.path.join(project_base, f'knowledge_base/{script}')
    if not os.path.exists(script):
        return False, "脚本文件不存在"
    code = open(script).read()
    return script_op(name, data, conf, input_params, output_params, code)


def get_basic_entity(conf, payload, data):
    entity_id = payload['id']
    ok, entity = get_entity_detail(entity_id, conf)
    if ok and entity:
        be_data = {}
        dataProperties = entity.get("dataProperties", [])
        for item in dataProperties:
            be_data[item["dpName"]] = item["dpValue"]

        entity = {
            "name": entity["name"],
            "be_data": be_data
        }

    return ok, entity
