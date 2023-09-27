## 环境准备
### 安装所需的库
```pip install happy-python pymongo```


### 更改配置文件
```bash
cd mongo-py
cp conf/config.ini.sample conf/config.ini
cp conf/log.ini.sample conf/log.ini
```

在config.ini中填写mongodb的ip和port

## 使用方法
1.使用文件上传，file.js中为json格式的内容

```python main.py -i file.js```


2.查询匹配{'name': 'Jordan'}的document

```python main.py -q "{'name': 'Jordan'}"```


3.将匹配{'name': 'Jordan'}的collection更改name为Mike

```python main.py -u "{'name': 'Jordan'}" "{'name':'Mike'}"```


4.删除匹配{'name':'Mike'}的所有document

```python main.py -d "{'name':'Mike'}"```






