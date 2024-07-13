"""
基于pyDatalog的Datalog规则引擎
"""

import os
from pyDatalog.pyDatalog import load, ask, Logic


project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def fact_value(v):
    if isinstance(v, str):
        return f"'{v}'"
    return v


class RuleEngine:
    def __init__(self, rule_id: str):
        # here use local file for now
        file_path = os.path.join(project_root, f'knowledge_base/{rule_id}.datalog')
        self.basic_rules = open(file_path).read().strip()

    def add_facts(self, subject, facts):
        rules = [self.basic_rules]
        for fact in facts:
            for k1, v1 in fact.items():
                if v1 is None:
                    continue
                if isinstance(v1, dict):
                    for k2, v2 in v1.items():
                        if not v2:
                            continue
                        rules.append(f"{k1}_{k2}['{subject}'] = {fact_value(v2)}")
                else:
                    rules.append(f"{k1}['{subject}'] = {fact_value(v1)}")
        self.basic_rules = '\n'.join(rules)

    def build(self):
        print(self.basic_rules)
        Logic()
        load(self.basic_rules)

    def ask(self, query):
        print("query", query)
        res = ask(query)
        if res:
            return list(res.answers)
        return []
