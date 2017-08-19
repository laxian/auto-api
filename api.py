
import json

class Api:

    def __init__(self, param):
        if isinstance(param,str):
            self.param=json.loads(param)
        elif isinstance(param, dict):
            self.param=param

    def api_name(self):
        return self.param['apiName']

    def method(self):
        return self.param['method']

    def path(self):
        return self.param['path']

    def params(self):
        return self.param['params']

    def param_list(self):
        return list(self.param['params'].keys())


if __name__=='__main__':
    api='''{
        "method": "get",
        "path": "classm",
        "apiName": "getUpClassInfo.do",
        "params": {
          "userId": "int",
          "classId": "int",
          "time": "long",
          "sign": "String"
        }
      }
    '''

    a=Api(api)
    print(a)
    print(a.api_name())
    print(a.method())
    print(a.path())
    print(a.params())
    print(a.param_list())