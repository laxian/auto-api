import random
import re
import time
import requests


def random_select(v):
    if isinstance(v, str) and re.match(r'{\d+(,[0-9]+)+}', v):
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
    if jpath is not None:
        paths = jpath.split('/')
        i = 0
        curr = jdic
        while i < len(paths):
            p = paths[i]
            if p.endswith('[]'):
                lst = curr[p.replace('[]', '')]
                random_index = random.randint(0, len(lst) - 1)
                curr = lst[random_index]
            else:
                curr = curr[p]
            i += 1
        return curr
    return None


if __name__ == '__main__':
    a='laxian is !{2+3} years old'
    for i in range(0,9):
        print(eval_all(a))