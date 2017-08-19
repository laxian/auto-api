import random
import re


def random_select(v):
    if re.match(r'{\d+(,[0-9]+)+}', v):
        lst = v[1:-1].split(',')
        index = random.randint(0, len(lst) - 1)
        return lst[index]
    return v



if __name__ == '__main__':
    a='{0,1}'
    for i in range(0,9):
        print(random_select(a))