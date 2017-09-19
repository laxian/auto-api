# -*- coding: utf-8 -*-
import re

import sys

__author__ = 'zwx'


class Argv(object):
    def __init__(self):
        pass

    @staticmethod
    def parse_list(argv_str, man=None):
        '''
        :param arg_str: eg:   xxx.py -p arg1 -s arg2 -f arg3
        :return: dict:  ['-p', 'arg1','-s', 'arg2','-f', 'arg3']
        '''

        argv_str = argv_str.strip()
        ss = re.findall('\s{2,}', argv_str)
        # 空格去重
        for s in ss:
            argv_str.replace(s, ' ')
        kw = argv_str.split(' ')
        return kw

    @staticmethod
    def parse_dict(argv_str, man=None):
        '''
        :param arg_str: eg:   xxx.py -p arg1 -s arg2 -f arg3 please make sure argv in pairs
        :return: dict:  {'-p':'arg1','-s':'arg2','-f':'arg3'}
        '''

        return Argv.parse_argv(Argv.parse_list(argv_str), man)

    @staticmethod
    def parse_argv(kw, man=None):
        '''
        解析项目命令行参数，第一个参数认为是name，-v出现则为True，否则为false。其余参数成对出现
        :param kw:
        :param man:
        :return:
        '''
        dic = {}
        dic['name'] = kw[0]
        i = 1
        while i < len(kw):
            if kw[i].startswith('-') or kw[i].startswith('/'):
                if kw[i] == '-v':
                    dic[kw[i]] = True
                    i += 1
                elif kw[i] == '-p':

                    cur = i + 1
                    if re.match('\w+\:\w+', kw[cur]):
                        pdic = {}
                        cur = i + 1
                        while cur < len(kw) and not kw[cur].startswith('-'):
                            kvp = kw[cur].split(':')
                            pdic[kvp[0]] = kvp[1]
                            cur += 1
                        dic[kw[i]] = pdic.__str__()
                        # print(kw[i])
                        i = cur
                    else:
                        # {type:1,age:2}
                        find_keys = re.findall('[{,]\s*(\w+)\:', kw[i + 1])
                        for k in find_keys:
                            kw[i + 1] = kw[i + 1].replace(k, "%r" % k)
                        dic[kw[i]] = kw[i + 1]
                        i += 2
                else:
                    dic[kw[i]] = kw[i + 1]
                    i += 2
            elif kw[i] == '':
                i += 1
            else:
                if man is None:
                    print('Illegal Argv: "%s"' % kw[i])
                    i += 1
                else:
                    print(man)
        return dic


if __name__ == '__main__':
    dic = Argv.parse_argv(sys.argv)
    print(dic)

    s = "argv.py addEnrollInfo.do -p studentLoginId:s1@66666888"
    dic2 = Argv.parse_dict(s)
    print(dic2)
