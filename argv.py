import re

import sys


class Argv(object):

    def __init__(self):
        pass

    @staticmethod
    def parse(argv_str, man=None):
        '''
        :param arg_str: eg:   xxx.py -p arg1 -s arg2 -f arg3
        :return: dict:  {'-p':'arg1','-s':'arg2','-f':'arg3'}
        '''

        argv_str=argv_str.strip()
        ss = re.findall('\s{2,}', argv_str)
        # 空格去重
        for s in ss:
            argv_str.replace(s, ' ')
        kw = argv_str.split(' ')
        return Argv.parse_argv(kw, man)

    @staticmethod
    def parse_argv(kw, man=None):
        dic = {}
        dic['name'] = kw[0]
        i = 1
        while i < len(kw):
            if kw[i].startswith('-') or kw[i].startswith('/'):
                dic[kw[i]] = kw[i + 1]
            else:
                if man is None:
                    print('format error')
                else:
                    print(man)
            i += 2
        return dic


if __name__ == '__main__':
    dic=Argv.parse_argv(sys.argv)
    print(dic)

    s='argv.py -p abcp -s ssss -f yes'
    dic2=Argv.parse(s)
    print(dic2)