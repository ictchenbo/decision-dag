class EvalNode:
    # Python内置布尔运算法，基于eval实现
    op_list = ['==', '<=', '>=', '<', '>', '!=']

    def __init__(self, expr: str):
        self.expr = expr
        self.op = None
        # 陆上机动装备类型[Y] == '越野汽车'
        for op in self.op_list:
            if op in expr:
                parts = expr.split(op)
                self.op = op
                self.left = parts[0]
                self.right = parts[1]
                break

    @staticmethod
    def replace(part: str, context):
        """
        将变量替换为实际值，例如 宽度[X]  --->   5.0
        :param part: 待替换的部分，如 宽度[X]
        :param context: 参数上下文
        :return: 返回替换后的值，如 5.0。注意，如果是字符串，需要添加引号，以便作为Python代码执行
        """
        part = part.strip()
        if part.endswith(']'):
            s_p = part.split('[')
            predicate = s_p[0]
            s_var = s_p[1][:-1]
            if s_var in context:
                props = context[s_var].get('props', {})
                if predicate in props:
                    v = props[predicate]
                    return f"'{v}'" if isinstance(v, str) else v
            return None
        return part

    def eval(self, context, errors: list):
        """
        根据输入数据进行表达式计算
        :param context: 绑定的参数实例
        :param errors: 错误输出
        :return:
        """
        if self.op is not None:
            left = EvalNode.replace(self.left, context)
            if left is None:
                errors.append(f'变量不匹配：{self.left}')
                return False
            right = EvalNode.replace(self.right, context)
            if right is None:
                errors.append(f'变量不匹配：{self.right}')
                return False
            expr = f'{left} {self.op} {right}'
        else:
            expr = EvalNode.replace(self.expr, context)
            if expr is None:
                errors.append(f'变量不匹配：{self.expr}')
                return False
        # Python内置的二元运算符 使用eval直接计算。另一种方式是
        res = eval(expr)
        if res is not None and not res:
            errors.append(f'{self.expr} ---> {expr}')
            print('Eval fail: ', self.expr, 'actual: ', expr)
        return res

    def __print__(self, level=0):
        for i in range(level):
            print(' ', end='')
        print(self.expr)


class RuleNode:
    def __init__(self, name, operator='AND'):
        self.name = name
        self.operator = operator
        self.params = {}
        self.children = []

    def add_param(self, param):
        self.params[param['variable']] = param

    def add_node(self, subnode):
        self.children.append(subnode)

    def eval(self, context, errors: list):
        """
        基于绑定的具体参数进行节点计算
        :param context:
        :param errors: 错误信息
        :return:
        """
        if not self.children:
            return True
        sub_errors = []
        if self.operator == 'OR':
            for child in self.children:
                if child.eval(context, sub_errors):
                    return True
            errors.extend(sub_errors)
            print('Eval fail: ', self.name)
            return False
        else:
            for child in self.children:
                if not child.eval(context, errors):
                    print('Eval fail: ', self.name)
                    return False
            return True

    def __print__(self, level=0):
        """
        打印规则节点，方便查看内容
        :param level: 级别 用于缩进
        :return:
        """
        for i in range(level):
            print(' ', end='')
        print(f'{self.name} {self.operator}(')
        for child in self.children:
            child.__print__(level + 1)
        for i in range(level):
            print(' ', end='')
        print(')')


class RuleTreeBuilder:
    def __init__(self, ruleset: dict):
        nodes = {}
        nodes_by_id = {}

        or_nodes = set()

        # 第一遍 初始化各节点
        for rule in ruleset["rules"]:
            name = rule["ruleName"]
            node = RuleNode(name)

            for term in rule["terms"]:
                node.add_param(term)

            if name not in nodes:
                nodes[name] = [node]
            else:
                nodes[name].append(node)

            if len(nodes[name]) > 1:
                or_nodes.add(name)

            nodes_by_id[rule["id"]] = node

        # 第二遍 名称相同的处理为OR关系
        for or_node_name in or_nodes:
            or_node = RuleNode(or_node_name, operator='OR')
            or_node.children = nodes[or_node_name]
            nodes[or_node_name] = [or_node]

        # 第三遍 建立上下级关系
        for rule in ruleset["rules"]:
            pnode = nodes_by_id[rule["id"]]
            for pre in rule["preConditions"]:
                pre = pre.strip()
                while pre.startswith('(') and pre.endswith(')'):
                    pre = pre[1:-1]
                if pre.endswith(')'):
                    sub_node_name = pre[:pre.find('(')]
                    if sub_node_name not in nodes:
                        print(f'NotFound: {sub_node_name}')
                    else:
                        pnode.add_node(nodes[sub_node_name][0])
                else:
                    pnode.add_node(EvalNode(pre))

        self.nodes_by_name = nodes
        self.nodes_by_id = nodes_by_id
        self.rule_json_def = ruleset

    def get_node(self, node_name=None, node_id=None):
        """
        根据id或名称获取节点，默认返回根节点
        :param node_name: 名称
        :param node_id: ID
        :return: 指定的节点
        """
        if node_id:
            return self.nodes_by_id.get(node_id)
        if node_name:
            if node_name not in self.nodes_by_name:
                return None
            return self.nodes_by_name[node_name][0]

        return self.nodes_by_id[self.rule_json_def['rules'][0]['id']]


def enum_list(output: list, target: dict, keys: list, array: list, index: int = 0):
    if index >= len(array):
        output.append(dict(target))
        return
    for item in array[index]:
        target[keys[index]] = item
        enum_list(output, target, keys, array, index+1)
        target.pop(keys[index])


def execute_rule(rule_tree: RuleNode, context: dict, query_binding: dict = {}):
    keys = []
    array = []
    for var, items in context.items():
        # 已绑定变量 不需要枚举
        if var in query_binding:
            continue
        keys.append(var)
        array.append(items)

    # 枚举变量组合
    combines = []
    enum_list(combines, {}, keys, array)

    # print('变量枚举：', combines)

    # 获得待绑定变量值 基于实体name
    context_map = {}
    for var, value in query_binding.items():
        found = list(filter(lambda x: x['name'] == value, context[var]))
        if len(found) == 0:
            return [], [f'failed to bind {var} = {value}']
        bind_instance = found[0]
        context_map[var] = bind_instance

    results = []
    errors = []
    # 枚举每个绑定实例
    for instance in combines:
        instance.update(**context_map)
        # print('当前上下文', instance)
        if rule_tree.eval(instance, errors):
            for var in query_binding.keys():
                instance.pop(var)
            results.append(instance)

    return results, errors
