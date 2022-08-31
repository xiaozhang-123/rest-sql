# query_ctrl

## 已知问题

1. onDataReceived(). 每次接受数据多次调用该回调函数。预估是grafana的问题。
2. select、where等字段提示错误。这部分官方代码参考价值不大，更改难度过大，暂时忽略。