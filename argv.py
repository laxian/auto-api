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
                if kw[i] == '-p':

                    cur = i+1
                    if re.match('\w+\:\w+', kw[cur]):
                        pdic={}
                        cur=i+1
                        while cur < len(kw) and not kw[cur].startswith('-'):
                            kvp=kw[cur].split(':')
                            pdic[kvp[0]]=kvp[1]
                            cur+=1
                        dic[kw[i]]=pdic.__str__()
                        i=cur
                    else:
                        #{type:1,age:2}
                        find_keys=re.findall('[{,]\s*(\w+)\:', kw[i+1])
                        for k in find_keys:
                            kw[i+1]=kw[i+1].replace(k, "%r"%k)
                        dic[kw[i]]=kw[i+1]
                        i+=2
                else:
                    dic[kw[i]] = kw[i + 1]
                    i+=2
            else:
                if man is None:
                    print('Illegal Argv: "%s"'%kw[i])
                    i+=1
                else:
                    print(man)
        return dic


if __name__ == '__main__':
    dic=Argv.parse_argv(sys.argv)
    print(dic)

    s="argv.py -p type:1 classId:2"
    dic2=Argv.parse(s)
    print(dic2)