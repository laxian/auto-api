#!/bin/python
# -*- coding: utf-8 -*-

from tasks import *

__author__ = 'zwx'


class Task(object):
    def __init__(self, dic, api):
        self.dic = dic
        self.api = api
        pass

    def name(self):
        return self.dic['name']

    def argv(self):
        return self.dic['argv']

    def assert_key(self):
        return ['code', 'resp', 'text', 'json']

    def asserts(self):
        assertExpr = self.dic['assert']
        return assertExpr

    def exec(self):
        response = Api.request_args(Argv.parse_dict('%s %s' % (self.name(), self.argv())))
        assert_expr = self.asserts()

        try:
            if '${result}' in assert_expr:
                assert_expr = assert_expr.replace('${result}', str(response) if response is not None else '')
                assert eval(assert_expr)
            if '${code}' in assert_expr:
                assert_expr = assert_expr.replace('${code}', str(response.status_code))
                assert eval(assert_expr)
            elif '${text}' in assert_expr:
                assert response.status_code == 200
                assert_expr = assert_expr.replace('${text}', response.text)
                assert eval(assert_expr)
            elif '${json}' in assert_expr:
                assert response.status_code == 200
                assert response.text
                jsn = json.loads(response.text)
                assert jsn
                argv_list = Argv.parse_list(assert_expr)[1:]
                if len(argv_list) > 0:
                    if '-j' in argv_list:
                        index_j = argv_list.index('-j')
                        find_v = utils.find_by_path(jsn, argv_list[index_j + 1])
                        if index_j + 2 < len(argv_list):
                            assert_expr = str(find_v) + assert_expr[assert_expr.find(argv_list[index_j + 2]):]
                        else:
                            assert_expr = find_v
                        assert eval(assert_expr)
                    else:
                        pass
            elif '${resp}':
                pass
            else:
                assert eval(self.asserts())
        except:
            print('\033[31m', end='')
            print('%-30s assert faild' % self.name())
            print('\033[0m', end='')
            return None
        print('\033[32m', end='')
        print('%-30s ok' % self.name())
        print('\033[0m', end='')


if __name__ == '__main__':
    tasksConfig = Tasks()
    tasks = tasksConfig.task_list()
    for t in tasks:
        t.exec()
