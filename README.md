# 决策推理服务
基于DAG的决策推理框架，决策流程从获取一组输入参数开始，按照DAG业务流程图执行一组决策节点，输出最终结果。
其中，决策节点为一个逻辑过程，包括：（1）执行计算表达式   （2）调用外部服务   （3）执行规则引擎进行推理  （4）调用外部脚本

## 快速使用
1. 安装Python依赖
```shell
pip install -r requirements.txt
```
2. 运行下列代码
```python
from decision_dag.reasoner import execute_process

r = execute_process("dag002", [
        {"name": "place_start", "value": "基隆港"},
        {"name": "place_end", "value": "松山机场"},
        {"name": "time_start", "value": "2022-12-11T04:00"},
        {"name": "troop", "value": "海军复兴号空降大队"}
    ])
print(r)

```

3. 启动Web服务
```shell
python server.py
```

4. 访问Web服务
```shell
curl -XPOST "http://localhost:8282/inference/_execute/dags" -H "Content-type: application/json" --data-binary '@mock_data/example_input_1.json'
```

## 开发计划
1. my_rule_engine存在多个版本 待测试、合并
2. 非统一接口的外部服务如何解析？引入jsonpath？


## 总体设计

1. 根据决策流程定义（从知识平台查询或加载本地`dag_{process_id}.json`文件），初始化流程图`Graph`
2. 输入参数预处理，准备好流程的上下文数据`context`
3. 每个决策节点根据节点类型执行具体操作：
  - 表达式，直接`eval`，结果附加到`context`中
  - 调用服务，根据`service_config.json`配置，获取匹配的服务，执行HTTP请求，结果附加到`context`中
  - 决策引擎，与服务调用类似，将当前上下文、获取的基础知识、获取的规则等，组成规则集，执行规则推理，并将推理结果(`ask`)附加到`context`中
  - 外部脚本，执行指定的脚本

## 数据结构
核心数据是流程的定义结构，示例如`dag_shore_land.json`文件，解释如下：

- `id` 流程ID
- `inputParams` 流程输入参数 表示流程能够接收的、作为初始化上下文的数据
- `outputParams` 流程输出参数 表示流程最后输出的结果
- `dagTasks` 决策节点列表 具体的中间节点
- `dagTasks[*].id` 节点标识
- `dagTasks[*].name` 节点名称
- `dagTasks[*].description` 节点描述
- `dagTasks[*].type` 节点类型，对应四种决策节点的逻辑过程，包括 `script | service | rule_engine | external_script `
- `dagTasks[*].script` 对应`script`类型节点的要执行的脚本
- `dagTasks[*].service` 对应`service`或`rule_engine`类型节点要调用的外部服务，形式为`<name>/<version>`，匹配服务名称及版本，版本可不限定
- `dagTasks[*].external_script` 对应`external_script`类型的外部脚本路径
- `dagTasks[*].inputParams` 对应`service`或`external_script`等类型节点的请求参数
- `dagTasks[*].outputParams` 定义节点输出
- `taskDependencies` 定义决策节点的依赖关系，从而可以构建DAG图，如果未指定则默认为`dagTasks`的串联图

## 详细设计

### 服务配置
通过`service_config.json`进行服务配置，支持名称、版本、描述、提供商、地址、请求方法、基本参数等信息

目前假设全部为http/restful接口，采用GET/POST方法请求，采用application/json传递参数

具体见`decition_reason/service_proxy.py`的`match_service`方法和`http_op`方法

### 参数提取
决策节点从上下文中获取参数，作为请求外部服务或执行脚本的参数，并且将配置的输出字段输出到上下文中

参考流程定义中决策节点的`inputParams`和`outputParams`字段，处理逻辑参考`decition_reason/service_proxy.py`的`extract_value`方法

```json
 {
   "time_ref": "@time",
   "place_literal": "地点A",
   "locations_list": ["@local", "地点A"],
   "params_dict": {"海洋环境": "@ocean"}
 }
```
参数值的类型：
- 字面值，字符串、数值、bool等
- @field，使用上下文的field
- 数组，形成对应的数组
- 字典，形成对应的字典，其中value符合前述定义

### 规则推理

### 决策推理执行

