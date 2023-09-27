# mongodb-tool

mongodb操作工具

## 环境准备

### 安装happy-python & pymongo
```bash
poetry install
```

## 单元测试

```bash
poetry run pytest -s
```

## 本地安装
```bash
poetry build -f wheel
pip install -U --user dist/zcx-*-py3-none-any.whl
```
列出 Python 包文件列表：
```bash
pip show zcx -f
```

终端输出：

    Name: zcx
    Version: 0.0.1
    Summary: Mongodb数据操作工具
    Home-page: https://github.com/Zcxx0322/mongodb-tool
    Author: Zcx
    Author-email: colampszcx@gmail.com
    License: 
    Location: /home/colamps/.local/lib/python3.11/site-packages
    Requires: happy-python, pymongo, pytest
    Required-by: 
    Files:
      ../../../bin/zcx
      __pycache__/main.cpython-311.pyc
      conf/config.ini.sample
      conf/log.ini.sample
      main.py
      method/__init__.py
      method/__pycache__/__init__.cpython-311.pyc
      method/__pycache__/file_create.cpython-311.pyc
      method/__pycache__/mongodb_base.cpython-311.pyc
      method/__pycache__/mongodb_dump.cpython-311.pyc
      method/__pycache__/mongodb_import.cpython-311.pyc
      method/file_create.py
      method/mongodb_base.py
      method/mongodb_dump.py
      method/mongodb_import.py
      var/log/error.log
      zcx-0.0.1.dist-info/INSTALLER
      zcx-0.0.1.dist-info/LICENSE
      zcx-0.0.1.dist-info/METADATA
      zcx-0.0.1.dist-info/RECORD
      zcx-0.0.1.dist-info/REQUESTED
      zcx-0.0.1.dist-info/WHEEL
      zcx-0.0.1.dist-info/direct_url.json
      zcx-0.0.1.dist-info/entry_points.txt
## 使用方法

获取命令行工具执行路径：

```bash
python -c "import site; print('%s/bin/zcx' % site.USER_BASE)"
```
终端输出：

    ~/.local/bin/zcx

### 运行

```bash
~/.local/bin/zcx
```

### 增加软链接
```bash
sudo ln -s ~/.local/bin/zcx /usr/local/bin/zcx
```

### 增加数据

```bash
zcx -i '{"name": "John", "age": 30, "city": "New York"}'
```

### 增加数据
```bash
zcx -i '{"name": "John", "age": 30, "city": "New York"}'
```

### 删除数据
```bash
zcx -d '{"name": "John", "age": 30, "city": "New York"}'
```

### 查找数据

#### 查找指定键值对数据
```bash
zcx -s '{"name": "John"}'
```

#### 查找集合中所有数据
```bash
zcx main.py -s 
```

### 修改数据
```bash
zcx -u '{"name": "John", "age": 34, "city": "Shanghai"}'
```
### 导入导出数据

#### 导出数据至指定文件
```bash
zcx --dump filename
```

#### 从指定文件导入数据
```bash
zcx --import filename
```

## 使用详细
请使用zcx --help/-h
```
$ zcx -h
2023-09-27 11:54:51 13771 [INFO] 未启用日志配置文件，加载默认设置
2023-09-27 11:54:51 13771 [INFO] 日志配置文件 '/home/colamps/.zcx/log.ini' 加载成功
2023-09-27 11:54:51 13771 [ERROR] 命令行参数错误，请查看使用说明：
usage: mongodb_tool [-c <config_file>] [-l <log_config_file>][-i <data>] [-d <data>] [-s <data>] [-u <data>] [--dump <filename>] [--import <filename>]

MongoDB工具

options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE        配置文件路径，默认为 ~/.zcx/config.ini
  -l LOG_CONFIG_FILE    日志配置文件路径，默认为 ~/.zcx/log.ini
  -i INSERT_DATA        执行插入操作，提供数据（JSON格式）
  -d DELETE_DATA        执行删除操作，提供查询条件（JSON格式）
  -s [SEARCH_DATA]      执行查询操作，提供查询条件（JSON格式）
  -u UPDATE_DATA        执行更新操作，提供查询条件和更新数据（JSON格式）
  --dump DUMP_FILE      导出数据到指定文件（JSON格式）
  --import IMPORT_FILE  从指定文件导入数据（JSON格式
```
