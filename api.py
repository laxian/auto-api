# -*- coding: utf-8 -*-

import json
import os
import random
import re
from collections import OrderedDict

import requests
import sys

import utils
from argv import Argv
from apis import Apis
from config import base_url, params_path

__author__ = 'zwx'


class Api:
    def __init__(self, api_info, verbose=False):
        self.counter = 0
        self.verbose = verbose
        if isinstance(api_info, str):
            self.api = json.loads(api_info, encoding='utf-8', object_pairs_hook=OrderedDict)
        elif isinstance(api_info, dict):
            self.api = api_info

        # 对于dict对象api来说，结构对应于params的一个api，对于其第一层key-value，如果有$xxx/xxx，或者@getApi ... 这类值，首先处理
        # $之后的语句，认为是一个路径，通过该路径可以找到json结构中的某个值，并引用。
        # @之后，认为是一个接口依赖，会首先请求，并把相应值挂在到json结构该处
        for k, v in api_info.items():

            if isinstance(v, str):
                if '$' in v:
                    # 匹配$a/b/c形式字符串
                    reg = '(\$(?:\*|[\w/]+))'
                    var_list = re.findall(reg, v)
                    for va in var_list:
                        rand = utils.random_select(utils.find_by_path(self.api, va[1:]))
                        v = v.replace(va, str(rand) if rand else '')
                    api_info[k] = v

            # 匹配@apiName形式字符串
            if isinstance(v, str) and v.startswith('@'):
                api_info[k] = self.request_cmd(v[1:])

    def params(self):
        '''
        "@if $type==1: '@getNewAccount.do {'type':3,'classId':$classId}' else"
        '''
        ps = self.api['params']
        for k in ps.keys():
            v = ps[k]

            if isinstance(v, dict) or isinstance(v, list):
                v = json.dumps(v)

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
                            ps[va[1:]] = rand if rand else ''
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

            # 准备废弃的语法
            if isinstance(v, str) and '@' in v:
                at_list = re.findall(r'@<<.+?>>', v)
                for al in at_list:
                    v = v.replace(al, self.request_cmd(al[3:-2]))

            ps[k] = v

        return {k: v for k, v in ps.items() if v is not None}

    def request_cmd(self, cmdline):
        '''
        用于请求当前apiA依赖的apiB，同时，apiB中可能需要引用apiA中的某个值，所以，需要将apiA作为参数传入
        :param cmdline: 命令行参数
        :return: 执行命令行的结果
        '''
        full_args = Argv.parse_dict(cmdline)
        return self.request_argv(full_args, self.api)

    @staticmethod
    def request_argv(args, pre_api=None):
        '''
        命令行参数解析成dict类型，并执行。参数里可以有$a/b/c 类型变量
        :param args: cmd参数组成的dict
        :return: 执行的结果
        '''
        param_dic = {}
        if '-p' in args.keys():
            v = args['-p']
            if re.match("\{('\w+'\s*:\s*'?\$?\w+'?)(?:\s*,\s*'\w+':\s*'?\$?\w+)*'?\}", v):
                '''
                预先加载的接口中，有$变量引用的，先替换变量，被应用的变量，需是常量，或者在引用之前被计算
                '''
                reg = '(\$(?:\*|[\w/]+))'
                var_list = re.findall(reg, v)
                # getStudentInfo.do -p {'studentId':$studentId}
                for va in var_list:
                    rand = utils.random_select(utils.find_by_path(pre_api, va[1:]))
                    v.replace(va, str(rand))
                param_dic['-p'] = v
            # -p {userId:1, loginId:123@qq, ...} 转化成dict
            if re.match("\{('\w+':\s*'?[\w@]+'?)(?:\s*,\s*'\w+':\s*'?[\w@]+'?)*}", v):
                param_dic = eval(v)

        # ready to request
        cfg = Apis()
        api_dic = cfg.find_api(args['name'])
        api_dic['params'].update(param_dic)
        newp = Api(api_dic, True if '-v' in args.keys() else False)
        return newp.request_and_find(args['-j'] if '-j' in args.keys() else None)

    # 拼接get请求url的参数部分
    def append_params(self, sep='?'):
        '''
        拼接请求参数，形如：?name=me&pwd=123456
        :param sep: 和base_url连接符，默认为'?'
        :return: ?name=me&pwd=123456
        '''
        dic = self.params()
        ret = sep
        for k in dic.keys():
            ret += k
            ret += '='
            ret += str(dic[k])
            ret += '&'
        return ret

    # 拼接post请求url
    def post_url(self):
        url = self.base_url() if self.base_url() else base_url
        return url + self.path() + self.api['apiName']

    # get请求url
    def get_url(self):
        pre_url = self.post_url()
        # 可能base_url里已经有了'?'。具体拼接方式，根据需求调整
        ret = self.post_url() + self.append_params('&' if '?' in pre_url else '?')
        return ret

    def base_url(self):
        return None if 'baseUrl' not in self.api else self.api['baseUrl']

    def name(self):
        return self.api['apiName']

    def method(self):
        return self.api['method']

    def path(self):
        return '' if 'path' not in self.api else self.api['path'] + os.sep

    def headers(self):
        return self.api['headers'] if 'headers' in self.api else None

    def request(self):
        '''
        请求地址返回Response对象
        :return: Response对象
        '''
        resp = None
        try:
            if self.method() == 'post':
                resp = requests.post(self.post_url(), data=self.params(), headers=self.headers())
            elif self.method() == 'get':
                resp = requests.get(self.get_url())
        except BaseException as e:
            self.printv(e)
        else:
            # 在输入-v命令时，打印返回值，或者请求失败信息
            self.printv(resp.text) if resp.status_code == 200 else self.printv('%s, %d', resp.reason, resp.status_code)
        return resp

    def request_and_find(self, jpath):
        '''
        请求，如果http code >= 400,输出错误并返回
        :param jpath: 路径
        :return: 返回路径查询结果，如果jpath为None，返回Response
        '''
        resp = self.request()
        return self.find_in_response(resp, jpath)

    def find_in_response(self, resp, jpath):
        if resp is None:
            return None
        if resp.status_code >= 400:
            return None
        if jpath is None:
            return resp
        txt = resp.text
        return self.find_in_json(jpath, txt)

    def find_in_json(self, jpath, jsn):
        '''
        从json字符串中，通过路径查找
        :param jpath: 路径以'/'分割，数组以'#'结尾
        :param jsn: json字符串
        :return: 查找结果，否则返回None
        '''
        try:
            jdic = json.loads(jsn)
            find_v = utils.find_by_path(jdic, jpath)
            return find_v if find_v is not None else None
        except:
            print('json 格式错误')
            return None

    def printv(self, *args):
        '''
        打印，只有在-v时有效。
        -v命令下，如果args只有一个值，输出该值，否则，第一个值为格式化字符串，后面的值为对应值
        :param args:
        :return:
        '''
        if self.verbose:
            if len(args) > 1:
                print(args[0] % args[1:])
            elif len(args) == 1:
                print(args[0])


if __name__ == '__main__':
    argv = Argv.parse_argv(sys.argv[1:])
    name = argv['name']
    cfg = Apis()
    api = cfg.find_api(name)
    p = Api(api)
    print(p.request())
