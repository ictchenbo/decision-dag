class LeafNode:
    def __init__(self, expr):
        """
         车宽[X] < 2.5
         车宽[X] < 路宽[Y]
         车宽[X]
        :param expr:
        """
        self.expr = expr

    def eval_node(self, data, errors: list):
        """
        1. 运算符

        expr = '2.0 < 2.5'

        data 字典
        {'X': {'aa车':{车宽：2.0, 车长：4.0}},  'Y': {'xx路':{路宽：2.0, 路长：4.0}}, 'Z': {} }
        :param data:
        :return:
        """
        opera_set = {'<=', '<', '==', '>=', '>', '!='}
        opera = None
        left, right = None, None  # left, right 为数字或者变量，变量需要从data中取值，数字直接赋值，之后在eval中进行计算
        if '<=' in self.expr:
            opera = '<='
            left, right = self.expr.split('<=')[0].strip(), self.expr.split('<=')[1].strip()  # 分割字符串
            left, right = left.strip(' '), right.strip(' ')  # 去除空格
        elif '>=' in self.expr:
            opera = '>='
            left, right = self.expr.split('>=')[0].strip(), self.expr.split('>=')[1].strip()
            left, right = left.strip(' '), right.strip(' ')
        elif '==' in self.expr:
            opera = '=='
            left, right = self.expr.split('==')[0].strip(), self.expr.split('==')[1].strip()
            left, right = left.replace(' ', ''), right.replace(' ', '')
            left, right = left.replace('\'', ''), right.replace('\'', '')  # 去除引号
        elif '<' in self.expr:
            opera = '<'
            left, right = self.expr.split('<')[0].strip(), self.expr.split('<')[1].strip()
            left, right = left.strip(' '), right.strip(' ')
        elif '>' in self.expr:
            opera = '>'
            left, right = self.expr.split('>')[0].strip(), self.expr.split('>')[1].strip()
            left, right = left.strip(' '), right.strip(' ')
        elif '!=' in self.expr:
            opera = '!='
            left, right = self.expr.split('!=')[0].strip(), self.expr.split('!=')[1].strip()
            left, right = left.replace(' ', ''), right.replace(' ', '')
            left, right = left.replace('\'', ''), right.replace('\'', '')  # 去除引号
        else:   # 如果没有运算符，那么就是一个变量，如车宽[X]
            opera = None
            left, right = self.expr.strip(' '), None
            left, right = left.replace('\'', ''), None  # 去除引号

        if left[-1] == ']':  # 如果是变量，那么需要从data中取值，车宽[X]
            name, var = left.split('[')[0].strip(), left.split('[')[1].strip(']')
            left = data[var]
            left = list(left.values())[0][name]  # 取出车宽的值
            # data[var]是一个字典，如{'X': {'aa车':{'陆上机动装备高度':2.0, '陆上机动装备宽度':4.0}},  'Y': {'xx路':{'道路限宽':2.0, '道路限高':4.0}}}
            # data['X']['xx车']['车宽']
        if right is not None and right[-1] == ']':
            name, var = right.split('[')[0].strip(), right.split('[')[1].strip(']')
            right = data[var]
            right = list(right.values())[0][name]

        if isinstance(left, (float, int)) or isinstance(right, (float, int)):  # 进行数值判断，如果是数字，则代表可以直接进行比较，使用eval函数
            left = str(left)
            right = str(right)
            expression = left + opera + right
            if eval(expression) is True:
                return True
            else:
                # print("当前未满足条件：", self.expr)
                errors.append(self.expr)
                return False
        else:
            if opera == '==':
                if left == right:
                    return True
                else:
                    # print("当前未满足条件：", self.expr)
                    errors.append(self.expr)
                    return False
            elif opera == '!=':
                if left != right:
                    return True
                else:
                    # print("当前未满足条件：", self.expr)
                    errors.append(self.expr)
                    return False



class TreeNode:
    def __init__(self, name, data_list=None, operation=None):
        self.name = name
        # self.data_list = data_list
        self.operation = operation
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def eval_node(self, data, errors: list):
        if self.operation == 'OR':
            for child in self.children:
                if child.eval_node(data, errors):
                    errors.clear()
                    return True
            return False
        elif self.operation == 'AND':
            for child in self.children:
                if not child.eval_node(data, errors):
                    return False
            return True
        # 哪个节点如果返回False，那么这个节点的父节点就不会再去判断其他节点的值，直接返回False，并且在当前节点输出该节点的名字


def load(data):  # 读取规则，并构造规则树
    node_list = []
    root_node = TreeNode(name=data['rules'][0]["ruleName"], operation='AND')
    node_list.append(root_node)
    hash_table = {}   # key是name value是节点
    hash_table[root_node.name] = []
    for rule in data['rules']:  # 这里将每个规则的前提条件作为一个节点
        if rule['ruleName'] != root_node.name and rule['ruleName'] not in hash_table:
            node_list.append(TreeNode(name=rule["ruleName"], operation='AND'))
            hash_table[rule["ruleName"]] = []
        hash_table[rule["ruleName"]].append(rule['preConditions'])

    for node in node_list:
        if len(hash_table[node.name]) == 1:
            for preCondition in hash_table[node.name][0]:
                preCondition = preCondition.split('(', 1)[0]  # 限制分割次数为1，只取最左边的'('
                for child_node in node_list:
                    if child_node.name == preCondition:
                        node.add_child(child_node)
                if '[' in preCondition and ']' in preCondition:
                    node.add_child(LeafNode(expr=preCondition))
        else:  # 两条规则的前提条件相同，但是规则名不同，会导致前提条件重复添加，operation='OR'
            node.operation = 'OR'
            for l in range(len(hash_table[node.name])):
                child_node = TreeNode(name=node.name, operation='AND')
                node.add_child(child_node)
                # 这里的name是规则名，因为有OR，所以规则名和上一个根节点是一样的，只不过上一个节点是AND，这里则是OR
                for preCondition in hash_table[node.name][l]:
                    if '[' in preCondition and ']' in preCondition:
                        child_node.add_child(LeafNode(expr=preCondition))
    return root_node


# 递归遍历树的每个节点
def traverse_tree(node, query):
    for child in node.children:
        if isinstance(child, LeafNode):
            continue
        if child.name == query:  #因为一定是函数名，所以不可能遍历叶子节点，一定是函数节点
            return child
        traverse_tree(child, query)  # 递归调用遍历子节点


def ask(root, data, query):
    query_function = query.split('(')[0]
    query_X = query.split('(')[1].split(',')[0].replace("'", '').replace(' ', '')
    query_Y = query.split('(')[1].split(',')[1].replace("'", '').replace(' ', '').replace(')', '')
    node = root
    errors = []
    if node.name != query_function:
        node = traverse_tree(node, query_function)
    print(node.eval_node(data, errors))
    if len(errors) != 0:
        print("当前未满足条件：", errors)
