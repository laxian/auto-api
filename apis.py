# -*- coding: utf-8 -*-

import json

from config import params_path

__author__ = 'zwx'


class Apis(object):
    '''
    加载接口参数配置文件类
    '''

    def __init__(self, param_path=params_path):
        f = open(param_path, 'r', encoding='utf-8')
        self.param_cfg = json.load(f)
        f.close()

    def get_param_dict(self, api_name):
        for p in self.param_cfg:
            if p['apiName'] == api_name:
                return p
        return None

    def param_config_list(self):
        return self.param_cfg

    def find_api(self, api_name):
        for p in self.param_config_list():
            if p['apiName'] == api_name:
                return p
        return None
