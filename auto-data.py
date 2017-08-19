# -*- coding: utf-8 -*-
import sys

from config import Config
from constant import params_path
from params import Param

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('---> please input api name and repeate num <---')
    else:
        api_name = sys.argv[1]
        num=1
        if len(sys.argv) == 3:
            num=int(sys.argv[2])
        cfg=Config(params_path)
        api = cfg.find_api(api_name)
        if api is None:
            print('---> api not exists <---')
        else:
            p=Param(api)
            for i in range(0,num):
                resp = p.request()
                print(resp.text)


