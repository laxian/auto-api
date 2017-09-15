# coding=utf-8
import json
import random
import re
import time
import requests

__author__ = 'zwx'


def random_select(v):
    if isinstance(v, str) and re.match(r'\{[\u4e00-\u9fa5\w]+(,[\u4e00-\u9fa5\w]+)*\}', v):
        lst = v[1:-1].split(',')
        index = random.randint(0, len(lst) - 1)
        return lst[index]
    return v


def eval_all(cmd):
    var_list = re.findall('!<<.+?>>', cmd)
    for va in var_list:
        cmd = cmd.replace(va, str(eval(va[3:-2])))
    var_list = re.findall('!\{\{.+?\}\}', cmd)
    for va in var_list:
        cmd = cmd.replace(va, str(eval(va[3:-2])))
    return cmd


def find_by_path(jdic, jpath):
    '''
    从字典中查找一个key。如果某一级是个str，但是path路径尚未走完，会尝试用json.loads加载str
    :param jdic: 例如： jpath：data/classId 在dict：{"data":{"classId":1}} 返回1；
            jpath：data/studentList#/studentId 在dict：{"data":{"studentList":[{"studentId":1},...]}}
            返回studentList里随机item下的studentId
    :param jpath: data/userInfo/interest#/name  以'#'结尾代表这是个list
    :return: 按jpath层级查找到的值，如果能找到。否则返回None
    '''
    if jpath is not None:
        paths = jpath.split('/')
        i = 0
        curr = jdic
        while i < len(paths):
            p = paths[i]
            if p.endswith('#'):
                p = p.replace('#', '')
                if p in curr:
                    lst = curr[p]
                    if len(lst) == 0:
                        return None
                else:
                    print('%r not in %r' % (p, curr))
                    return None
                if i == len(paths) - 1:
                    return curr
                # 非空list、非终点
                else:
                    # 直接子key检测过滤
                    lst = [x for x in lst if paths[i + 1].replace('#', '') in x]
                    if len(lst) == 0:
                        return None
                    if paths[i + 1].endswith('#'):
                        curr = {}
                        nlst = []
                        for l in lst:
                            nlst.extend(l[paths[i + 1].replace('#', '')])
                        curr[paths[i + 1].replace('#', '')] = nlst
                        a = 10
                    else:
                        lst = curr[p]
                        random_index = random.randint(0, len(lst) - 1)
                        curr = lst[random_index]

            else:
                if isinstance(curr, dict):
                    if p in curr.keys():
                        curr = curr[p]
                    else:
                        print('%r not in %r' % (p, curr))
                        return None
                else:
                    try:
                        curr = json.loads(curr)
                        curr = curr[p]
                    except:
                        print('%r not in %r' % (p, curr))
                        return None
            i += 1
        return curr
    return jdic


if __name__ == '__main__':
    a = 'laxian is !{2+3} years old'
    for i in range(0, 9):
        print(eval_all(a))
