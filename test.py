# -*- coding: utf-8 -*-
import json
import sys

import utils
from argv import Argv
from config import Config
from constant import params_path
from params import Param

if __name__ == '__main__':
    man = '''
    a tools auto test http api

    usage:
        auto-data.py <api_name> [-j json path] [-p params] [-r repeat]

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
        for i in range(0, r):
            print('\n-------->\n')
            rep=Param.request_argv(argv)
            jrep=json.loads(rep)
            if jrep['result']==22:
                newId=utils.find_by_path(jrep, 'data/newLogin')
