# auto-data.py

+ 自动接口测试，自定义接口依赖

1. $params/type, 引用json中params下type的值 {"params":{"type":1}}
2. !{{}}和!<<>>中的代码会被执行
3. @后面的代码
4. {1,2,...}中的值，随机选择
  + if xxx: else: xxx
  + apiName -p {dict} -j data/classList[]/classId
  请求接口apiName，apiName必须在配置文件中
  -p指定某些参数，同时也会读取配置参数。指定参数优先于配置参数
  -j指定取值路径，从取值路径中取值。如果某一级路径以'[]'结尾，说明是一个json array，从array中随机取值

执行顺序
1. 处理$xxx 变量替换
2. !{{}} !<<>> 代码块执行
3. if else 代码块执行