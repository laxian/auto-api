# -*- coding: utf-8 -*-
import sys

from argv import Argv
from config import Config
from constant import params_path
from params import Param



if __name__ == '__main__':
    man = '''
    a tools auto test http api
    
    usage:
        auto-data.py <api_name> [-r repeat] [-j json path] [-p params]
    
    example:
        python auto-data.py getXXX.do -r 5
        
    '''
    argv = Argv.parse_argv(sys.argv[1:])
    name = argv['name']
    cfg = Config(params_path)
    api = cfg.find_api(name)
    if api is None:
        print(man)
    else:
        r = int(argv['-r']) if '-r' in argv else 1
        for i in range(0,r):
            print('\n-------->\n')
            print(Param.request_argv(argv))