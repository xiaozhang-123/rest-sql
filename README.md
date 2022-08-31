#Rest-sql
使用Python Django 作为服务端框架框架，可在grafana配置或者http发送行如rest形式的sql请求。服务端接收处理，调用restsql中间件解析json请求，权限检查，并转化为对应的数据源sql请求（目前支持es,pgsql/mysql,druid)。数据返回后封装为统一的dataframe数据返回给前端展示。

因此用户在获取后台数据源的时候，可以不考虑来自业务的不同数据库查询，数据返回，权限处理，数据库连接等工作以及细节差异，这些均可由rest中间件进行处理。仅需一个查询rest-sql json，就可以获取不同数据库的数据

## 使用举例
现要对后台的sale表发起一个类似于sql请求： （test.sale 连接需要在中间件中进行配置)
```
select DATE_FORMAT(cu.created_at, '%Y-%m-%d') as buckettime, sum(price) as '总额',count(orderid) as '订单数' from sala where create_time between '2021-07-20 00:00:00' and '2021-07-30 00:00:00' group by buckettime limit 10000
```

那么用户在前端发起的请求如下
```json
{
    "from":"test.sale",
    "time":{
      "column":"create_time",
      "begin":"2021-7-20",
      "end":"2021-7-30",
      "interval":"86400"
    },
    "select":[
      {
        "column":"price",
        "alias":"总额",
        "metric":"sum"
      },
      {
        "column":"orderid",
        "alias":"订单数",
        "metric":"count"
      }
    ],
    "where":[],
    "group":[],
     "limit":1000
  }
```

## 对需要查询时序数据的时间段处理
时间单位描述
   
|时间单位|描述|示例|
| ----------- | ----------- | ----------- |
| S      | 秒       | [00,60]S|
| H      | 时       | [00,23]H|
| T      | 分       | [00,59]T|
| D      | 天       | 1D|
| M      | 月       | 1M|
| Y      | 年       | 1Y|
(如果该单位与其他数据源不一致，可以在内部再转换，与其他数据源处理同步)

#### todo
处理配置文件绝对路径存放
考虑‘配置文件由configmap挂载到镜像路径后传入’ 的问题

