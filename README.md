# 1. auto-api.py

    自动接口测试，自定义接口依赖。
    将待测试api的相关信息配置到json文档中，通过读取配置，请求接口，处理依赖

json配置格式

    [
        {
            "method": "get",
            "apiName": "getConfig.do",
            "params": {
              "appId": "561",
              "deviceCode": "SKGMHAGQ99999999",
              "time": "!{{int(time.time()*1000)}}",
              "sign": "!{{requests.post('http://school.xxxxxx.com/dl910ta/_ImTest/_manager/GenderCourseRecordSign.jsp', !<<dict($*,**{'method':'$apiName'})>>).text.strip()}}"
            }
        }
    ]

+ "$"符号，表示引用一个值，后面跟一个路径。eg: $params/type, 引用json中params下type的值 {"params":{"type":1}}
    $* 表示其他所有同级param，不包含自己。适用于生成sign的场景。sign使用其他所有参数生成(可能加盐)
+ !{{}}和!<<>>中的代码会被执行。可以嵌套
+ @后面的代码：
    * 是if else 语句，格式：*if xxx: else: xxx*。if后面的条件会被eval()函数执行，为真则取if后面的字符串值，否则取else语句的字符串值。若字符串以"@"开始，递归执行
    * 是一个接口名，则接口会被执行
+ {1,2,...}中的值，随机选择
+ 
+ apiName -p {dict} -j data/classList#/classId -v
  请求接口apiName，apiName必须在配置文件中
  -p指定某些参数，同时也会读取配置参数。指定参数优先于配置参数
  -j指定取值路径，从取值路径中取值。如果某一级路径以'#'结尾，说明是一个json array，从array中随机取值
    -j 后的路径，如果数组没有在路径最后，比如：-j a/list#/c, 假设，list中，有部分值（非全部）不存在c，则，list会从存在c的值得集合中随机选择。
    除非list中任意值都不包含c
  -v指定是否打印详细信息，若请求成功，会打印返回字符串信息，若失败，会打印失败原因和状态字
  对于一个路径，以a/b#/c为例，假设c可以为null，(即不存在)，但不全为null，则，a/b#/c不为null。因为路径中存在c，则会排除不含c的数组b中的项。

执行顺序
1. 处理$xxx 变量替换
2. !{{}} !<<>> 代码块执行
3. if else 代码块执行

## sample
    python auto-api.py 执行所有接口
    python auto-api.py login.do 执行login.do 接口
    python auto-api.py -p userId:1

# 2. task.py
批量执行接口，并设置断言

## task.json 配置
    [
      {
        "name": "login.do",
        "argv": "-p pwd:123456",
        "assert": "${result} == 1"
      },
      {
        "name": "getConfig.do",
        "argv": "",
        "assert": "'成功' in ${json} -j msg"
      },
      {
        "name": "getProtocolConfig.do",
        "argv": "",
        "assert": "${json} -j data/isUsedSecurity == 1"
      },
      {
        "name": "getWorkInfo.do",
        "argv": "-j data/classTypeList#/classType",
        "assert": "${result}  == 0"
      }
    ]

argv 格式同上，支持-p/-j/-v

## 断言
常量
+ ${code} 代表 http code
+ ${json} 代表 Response.text, json格式， 可通过-j path/to/some/key 提取value
+ ${text} 代表 Response.text
+ ${result} 代表 -j data/xxx 获取某个key的value
+ ${resp} 代表 Response本身，咱未实现

## sample

python task.py

## output
    login.do                       assert faild
    getConfig.do                   ok
    getProtocolConfig.do           ok
    getWorkInfo.do                 ok