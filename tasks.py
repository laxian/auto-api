#!/bin/python
# -*- coding: utf-8 -*-
import json

import utils
from argv import Argv
from apis import Apis
from constant import task_path
from api import Api
from task import Task

__author__ = 'zwx'


class Tasks(object):
    '''
    加载任务参数配置文件类
    '''

    def __init__(self, path=task_path):
        f = open(path, 'r', encoding='utf-8')
        self.tasks = json.load(f)
        self.apis = Apis()
        f.close()

    def find(self, task):
        return self.tasks[task] if task in self.tasks else None

    def task_list(self):
        tasks = []
        for t in self.tasks:
            api = self.apis.find_api(t['name'])
            task = Task(t, api)
            tasks.append(task)
        return tasks


if __name__ == '__main__':
    pass
