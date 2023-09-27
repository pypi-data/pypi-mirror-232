# mongodb-tool

mongodb操作工具

## 环境准备

### 安装happy-python & pymongo
```bash
pip install happy-python

python -m pip install "pymongo[srv]" --trusted-host pypi.tuna.tsinghua.edu.cn
```

## 单元测试

```bash
cd tests && pytest
```

## 使用举例

### 增加数据

```bash
python main.py -i '{"name": "John", "age": 30, "city": "New York"}'
```

### 增加数据
```bash
python main.py -i '{"name": "John", "age": 30, "city": "New York"}'
```

### 删除数据
```bash
python main.py -d '{"name": "John", "age": 30, "city": "New York"}'
```

### 查找数据

#### 查找指定键值对数据
```bash
python main.py -s '{"name": "John"}'
```

#### 查找集合中所有数据
```bash
python main.py -s 
```

### 修改数据
```bash
python main.py -u '{"name": "John", "age": 34, "city": "Shanghai"}'
```
### 导入导出数据

#### 导出数据至指定文件
```bash
python main.py --dump filename
```

#### 从指定文件导入数据
```bash
python main.py --import filename
```

## 使用详细
请使用python main.py --help/-h
```
$ python main.py -h
2023-09-26 14:40:07 10537 [INFO] 未启用日志配置文件，加载默认设置
2023-09-26 14:40:07 10537 [INFO] 日志配置文件 '/home/colamps/workspace/github/mongodb-tool/method/../conf/log.ini' 加载成功
usage: mongodb_tool [-i <data>] [-d <data>] [-s <data>] [-u <data>] [--dump <filename>] [--import <filename>]

MongoDB工具

options:
  -h, --help            show this help message and exit
  -i INSERT_DATA        执行插入操作，提供数据（JSON格式）
  -d DELETE_DATA        执行删除操作，提供查询条件（JSON格式）
  -s [SEARCH_DATA]      执行查询操作，提供查询条件（JSON格式）
  -u UPDATE_DATA        执行更新操作，提供查询条件和更新数据（JSON格式）
  --dump DUMP_FILE      导出数据到指定文件（JSON格式）
  --import IMPORT_FILE  从指定文件导入数据（JSON格式）
```
