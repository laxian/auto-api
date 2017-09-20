#!/bin/python
# -*- coding: utf-8 -*-
import sys

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

    def exec(self, verbose=False):

        '''
        执行一个接口任务，并断言
        :return: 断言成功返回True，否则返回False
        '''

        response = Api.request_argv(Argv.parse_dict('%s%s %s' % (self.name(), ' -v ' if verbose else '', self.argv())))
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
            print('\033[32m', end='')
            print('%-30s ok' % self.name())
            print('\033[0m', end='')
            return True
        except:
            print('\033[31m', end='')
            print('%-30s assert (%s) faild.' % (self.name(), assert_expr))
            print('\033[0m', end='')
            return False


if __name__ == '__main__':
    verbose = False
    if len(sys.argv) > 1 and '-v' in sys.argv:
        verbose = True
    tasksConfig = Tasks()
    tasks = tasksConfig.task_list()
    success, fail = 0, 0
    for t in tasks:
        if t.exec(verbose):
            success += 1
        else:
            fail += 1

    print('\nsuccess:%10d'%(success))

    # 统计，失败红色高亮
    print('\033[1;31m', end='')
    print('fail   :%10d'%(fail))
    print('\033[0m', end='')
