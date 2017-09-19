# -*- coding: utf-8 -*-
import sys

from argv import Argv
from apis import Apis
from config import params_path
from api import Api

__author__ = 'zwx'

if __name__ == '__main__':
    man = '''
    a tools auto test http api
    
    usage:
        auto-api.py <api_name> [-j json path] [-p params] [-r repeat]
    
    example:
        python auto-api.py getXXX.do -r 5
        
    '''
    cfg = Apis()
    if len(sys.argv) > 1:
        argv = Argv.parse_argv(sys.argv[1:])
        name = argv['name']
        api = cfg.find_api(name)
        if api is None:
            print(man)
        else:
            r = int(argv['-r']) if '-r' in argv else 1
            for i in range(0, r):
                print('\n %r -->\n' % name)
                result = Api.request_argv(argv)
                if result:
                    print(result)
    else:
        for p in cfg.param_cfg:
            name = p['apiName']
            print('\n %r -->\n' % name)
            result = Api.request_argv({'name': name})
            if result:
                print(result)
