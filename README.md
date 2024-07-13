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


## 其他
[设计文档](docs/design.md)
