import functools

import requests

sign_url = 'http://www.yuwenclub.com/dyw-managet/test/_manager/GenderCourseRecordSign.jsp'


def get_sign(dic, url=sign_url):
    response = requests.post(url, data=dic)
    return response.text.strip()





if __name__ == '__main__':
    sign = functools.partial(get_sign, url=sign_url)
    dic={"userId":1, "schoolId":1, "type":2, "time":"1502964578608", "method":"getNewAccount.do"}
    s=sign(dic)
    print(s)
