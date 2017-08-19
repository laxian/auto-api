# -*- coding: utf-8 -*-

import json
import os
import random
import re
import time

import requests

import utils
from config import Config
from constant import base_url
from sign import get_sign


class Param:

    jpath = None

    def __init__(self, param):
        self.counter=0
        if isinstance(param, str):
            self.param = json.loads(param, encoding='utf-8')
        elif isinstance(param, dict):
            self.param = param

    def params(self):
        '''
        "@if $type==1: '@getNewAccount.do {'type':3,'classId':$classId}' else None"
        '''
        ps=self.param['params']
        for k in ps.keys():
            v=ps[k]
            if isinstance(v, str) and v.startswith('@'):
                cmd=v[1:]
                if '$' in cmd:
                    var_list=re.findall('(\$\w+)',cmd)
                    for va in var_list:
                        rand=utils.random_select(ps[va[1:]])
                        ps[va[1:]]=rand
                        cmd=cmd.replace(va, rand)
                if cmd.startswith('if'):
                    if_start=cmd.find(':',cmd.index('if'))+1
                    if_end = len(cmd)
                    else_sentence=None
                    if cmd.find('else') != -1:
                        if_end=cmd.find('else',if_start)
                        else_start=cmd.find('else:')
                        else_sentence=cmd[else_start+len('else:'):].strip()
                    if_cmd=cmd[len('if'):if_start-1].strip()
                    if_sentence=cmd[if_start:if_end].strip()
                    if eval(if_cmd):
                        ps[k]=if_sentence
                    else:
                        ps[k]=else_sentence

        return ps

    def append_params(self):
        dic = self.params_conv()
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

    def params_conv(self):
        '''
            "params": {
              "userId": 1,
              "type": "{1,2,3}",
              "schoolId": 1,
              "classId": null,
              "time": "@now",
            }
        :return:
        '''
        dic = self.params()
        dic2 = {}
        for k in dic:
            v = dic[k]
            if v is None:
                continue
            if isinstance(v, str):
                if re.match(r'{\d+(,[0-9]+)+}', v):
                    dic2[k] = utils.random_select(v)
                elif v.__contains__('%'):
                    dic2[k] = v % (self.counter)
                else:
                    dic2[k] = v
                if v.startswith('@'):
                    v=v[1:]
                    ss=re.findall('\s{2,}', v)
                    #空格去重
                    for s in ss:
                        v.replace(s, ' ')
                    kw=v.split(' ')
                    api=kw[0]
                    kw.remove(api)
                    i=0
                    param=None
                    jpath=None
                    param_dic=None
                    while i < len(kw):
                        if kw[i]=='-p':
                            param=kw[i+1]
                            i+=1
                        elif kw[i]=='-j':
                            jpath=kw[i+1]
                            i+=1
                        i+=1
                    if re.match('\{[:\'",\w]+\}',param):
                        param_dic=eval(param)

                    # ready to request
                    cfg=Config()
                    api_param=cfg.find_api(api)
                    api_param_param=dict(api_param['params'], **param_dic)
                    api_param['params']=api_param_param
                    newp=Param(api_param)
                    newp.set_jpath(jpath)
                    dic2[k]=newp.pick()

            else:
                dic2[k] = v

        dic2['time'] = int(time.time() * 1000)
        dic2['method'] = self.api()
        dic2['sign'] = get_sign(dic2)
        del dic2['method']

        self.counter+=1
        return dic2

    def post_url(self, url=base_url):
        return url + self.path() + self.param['apiName']

    def get_url(self, url=base_url):
        ret = self.post_url() + self.append_params()
        print(ret)
        return ret

    def request(self):
        if self.method()=='post':
            return requests.post(self.post_url(),data=self.params_conv())
        elif self.method()=='get':
            return requests.get(self.get_url())

    def set_jpath(self, jpath):
        self.jpath=jpath

    def pick(self):
        if self.jpath is not None:
            resp=self.request()
            jdic=json.loads(resp.text)
            paths = self.jpath.split('/')
            i=0
            curr=jdic
            while i < len(paths):
                p=paths[i]
                if p.endswith('[]'):
                    lst=curr[p.replace('[]','')]
                    random_index=random.randint(0, len(lst)-1)
                    curr=lst[random_index]
                else:
                    curr=curr[p]
                i+=1
            return curr


# if __name__ == '__main__':
#
#     ps = '''
#       {
#     "method": "get",
#     "apiName": "getNewAccount.do",
#     "params": {
#       "userId": 1,
#       "type": "{1,2,3}",
#       "schoolId": 1,
#       "classId": null
#     }
#   }
#   '''
#
#     p = Param(ps)
#     for i in range(0, 10):
#         pdic = p.params_conv(i)
#         res = requests.get(p.get_url())
#         print(res.text)

#
# if 1==1:
#      print("@getNewAccount.do {'type':3,'classId':$classId}")
#  else:
#      print(None)
#
# '''if 1==1: \n\t"ret=@getNewAccount.do {'type':3,'classId':$classId}" \nelse: \n\tret=None'''
