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
    def __init__(self, api):
        self.counter = 0
        if isinstance(api, str):
            self.api = json.loads(api, encoding='utf-8', object_pairs_hook=OrderedDict)
        elif isinstance(api, dict):
            self.api = api

        #如果有预先加载接口，首先加载
        for k,v in api.items():
            if isinstance(v, str) and v.startswith('@'):
                api[k]=self.request_cmd(v[1:])

    def params(self):
        '''
        "@if $type==1: '@getNewAccount.do {'type':3,'classId':$classId}' else None"
        '''
        ps = self.api['params']
        for k in ps.keys():
            v = ps[k]

            if not isinstance(v, str):
                continue

            if '%' in v:
                v = v % (self.counter)

            if re.match(r'\{[\u4e00-\u9fa5\w]+(,[\u4e00-\u9fa5\w]+)*\}', v):
                v = utils.random_select(v)

            # 1. 处理$变量
            if '$' in v:
                reg = '(\$(?:\*|[\w/]+))'
                var_list = re.findall(reg, v)
                for va in var_list:

                    if va == '$*':
                        del ps[k]
                        # print(ps)
                        v = v.replace(va, json.dumps({k: v for k, v in ps.items() if v is not None}))
                        ps[k] = v
                    else:
                        rand = utils.random_select(utils.find_by_path(self.api, va[1:]))
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

            if isinstance(v, str) and '@' in v:
                at_list = re.findall(r'@<<.+?>>', v)
                for al in at_list:
                    v = v.replace(al, self.request_cmd(al[3:-2]))

            ps[k] = v

        return {k: v for k, v in ps.items() if v is not None}

    def request_cmd(self, cmd):
        param = Argv.parse(cmd)
        return self.request_argv(param, self.api)

    @staticmethod
    def request_argv(param, api=None):
        param_dic = {}
        if '-p' in param.keys():
            v = param['-p']
            if re.match("\{('\w+':\s*'?[\w@]+'?)(?:\s*,\s*'\w+':\s*'?[\w@]+'?)*}", v):
                param_dic = eval(v)
            elif re.match("\{('\w+':\s*'?\$\w+'?)(?:\s*,\s*'\w+':\s*'?\$\w+'?)*}", v):
                '''
                预先加载的接口中，有$变量引用的，先替换变量，被应用的变量，需是常量，或者在引用之前被计算
                '''
                reg = '(\$(?:\*|[\w/]+))'
                var_list = re.findall(reg, v)
                #getStudentInfo.do -p {'studentId':$studentId}
                for va in var_list:
                    rand = utils.random_select(utils.find_by_path(api, va[1:]))
                    param_dic = eval(v.replace(va, str(rand)))


        # ready to request
        cfg = Config()
        api_dic = cfg.find_api(param['name'])
        api_dic['params'].update(param_dic)
        newp = Param(api_dic)
        return newp.request_and_find(param['-j'] if '-j' in param.keys() else None)

    # 拼接get请求url的参数部分
    def append_params(self):
        dic = self.params()
        ret = '?'
        for k in dic.keys():
            ret += k
            ret += '='
            ret += str(dic[k])
            ret += '&'
        return ret

    # 拼接post请求url
    def post_url(self, url=base_url):
        return url + self.path() + self.api['apiName']

    # get请求url
    def get_url(self, url=base_url):
        ret = self.post_url() + self.append_params()
        print(ret)
        return ret

    def api(self):
        return self.api['apiName']

    def method(self):
        return self.api['method']

    def path(self):
        return '' if 'path' not in self.api else self.api['path'] + os.sep

    def request(self):
        if self.method() == 'post':
            return requests.post(self.post_url(), data=self.params())
        elif self.method() == 'get':
            return requests.get(self.get_url())

    def request_and_find(self, jpath):
        resp = self.request()
        jsn = resp.text
        return self.find_in_json(jpath, jsn)

    def find_in_json(self, jpath, jsn):
        jdic = json.loads(jsn)
        find_v=utils.find_by_path(jdic, jpath)
        return find_v if find_v else jsn

