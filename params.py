# -*- coding: utf-8 -*-

import json
import os
import random
import re
from collections import OrderedDict

import requests

import utils
from argv import Argv
from config import Config
from constant import base_url


class Param:
    def __init__(self, param):
        self.counter = 0
        if isinstance(param, str):
            self.param = json.loads(param, encoding='utf-8', object_pairs_hook=OrderedDict)
        elif isinstance(param, dict):
            self.param = param

    def params(self):
        '''
        "@if $type==1: '@getNewAccount.do {'type':3,'classId':$classId}' else None"
        '''
        ps = self.param['params']
        for k in ps.keys():
            v = ps[k]

            if not isinstance(v, str):
                continue

            if '%' in v:
                v = v % (self.counter)

            if re.match(r'{\d+(,[0-9]+)+}', v):
                v = utils.random_select(v)

            # 1. 处理$变量
            if '$' in v:
                reg = '(\$(?:\*|[\w/]+))'
                var_list = re.findall(reg, v)
                for va in var_list:

                    if va == '$*':
                        del ps[k]
                        print(ps)
                        v = v.replace(va, json.dumps({k: v for k, v in ps.items() if v is not None}))
                        ps[k] = v
                    else:
                        rand = utils.random_select(utils.find_by_path(self.param, va[1:]))
                        if va[1:] in ps.keys():
                            ps[va[1:]] = rand
                        v = v.replace(va, str(rand))

            # 1. 可执行代码块
            if re.findall('!\{\{.+?\}\}', v):
                if re.findall('!\{\{.+?\}\}', v) or re.findall('!<<.+?>>', v):
                    v = utils.eval_all(v)

            # @后面的代码
            if v.startswith('@'):

                while isinstance(v, str) and v.startswith('@'):
                    cmd = v[1:]
                    if cmd.startswith('if '):
                        if_start = cmd.find(':', cmd.index('if')) + 1
                        if_end = len(cmd)
                        else_sentence = None
                        if cmd.find('else') != -1:
                            if_end = cmd.find('else', if_start)
                            else_start = cmd.find('else:')
                            else_sentence = cmd[else_start + len('else:'):].strip()
                        if_cmd = cmd[len('if'):if_start - 1].strip()
                        if_sentence = cmd[if_start:if_end].strip()
                        if eval(if_cmd):
                            v = if_sentence
                        else:
                            v = else_sentence
                    else:
                        v = self.request_cmd(cmd)

            if v is not None:
                ps[k] = v
            else:
                del ps[k]

        return ps

    def request_cmd(self, cmd):
        param = Argv.parse(cmd)
        return self.request_argv(param)

    @staticmethod
    def request_argv(param):
        param_dic = {}
        if '-p' in param.keys():
            if re.match("\{('\w+':\s*'?\w+'?)(?:\s*,\s*'\w+':\s*'?\w+'?)*}", param['-p']):
                param_dic = eval(param['-p'])

        # ready to request
        cfg = Config()
        api_param = cfg.find_api(param['name'])
        print('____> %r'%api_param)
        print('____> %r'%param_dic)
        api_param['params'].update(param_dic)
        print('+++++ %r'%api_param)
        newp = Param(api_param)
        return newp.pick(param['-j'] if '-j' in param.keys() else None)

    def append_params(self):
        dic = self.params()
        ret = '?'
        for k in dic.keys():
            ret += k
            ret += '='
            ret += str(dic[k])
            ret += '&'
        return ret

    def api(self):
        return self.param['apiName']

    def method(self):
        return self.param['method']

    def dependency(self):
        return self.param['dependency'] if 'dependency' in self.param else None

    def path(self):
        return '' if 'path' not in self.param else self.param['path'] + os.sep

    def post_url(self, url=base_url):
        return url + self.path() + self.param['apiName']

    def get_url(self, url=base_url):
        ret = self.post_url() + self.append_params()
        print(ret)
        return ret

    def request(self):
        if self.method() == 'post':
            return requests.post(self.post_url(), data=self.params())
        elif self.method() == 'get':
            return requests.get(self.get_url())

    def pick(self, jpath):
        resp = self.request()
        jsn = resp.text
        if jpath is not None:
            jdic = json.loads(jsn)
            paths = jpath.split('/')
            i = 0
            curr = jdic
            while i < len(paths):
                p = paths[i]
                if p.endswith('#'):
                    lst = curr[p.replace('#', '')]
                    random_index = random.randint(0, len(lst) - 1)
                    curr = lst[random_index]
                else:
                    print('--->%r' % curr)
                    curr = curr[p]
                i += 1
            return curr
        return jsn
