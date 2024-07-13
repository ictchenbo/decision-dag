#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict

logging.basicConfig(
        format="[%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s"
    )
logging.getLogger().setLevel(logging.DEBUG)


class Op(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func


start_op = Op('start_op', lambda x, y, z: logging.info('Start!'))
finish_op = Op('finish_op', lambda x, y, z: logging.info('Finish!'))
join_op = Op('join_op', lambda x, y, z: logging.info('Join %s!' % x))


class OpManager(object):
    def __init__(self):
        self.op_collection = OrderedDict({
            'start_op': start_op,
            'finish_op': finish_op,
            'join_op': join_op
        })

    def add(self, op: Op):
        assert isinstance(op, Op), 'Input op is not Op class.'
        if op.name in self.op_collection:
            return False
        self.op_collection[op.name] = op
        return True

    def get(self, name):
        return self.op_collection.get(name)

    def list(self):
        return list(self.op_collection.keys())
