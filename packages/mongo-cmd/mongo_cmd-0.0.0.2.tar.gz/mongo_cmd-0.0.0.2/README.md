# geekcamp-calculator
一款mongodb 命令行操作工具

## 环境准备

```bash
pip install --upgrade build twine

```
改写pyproject.toml文件


## 本地安装

```bash
poetry -m build 
```

列出 Python 包文件列表：

```bash
pip show mongo-cmd  -f
```

### 运行

```bash
~/.mongo

### 操作界面

1. Exit
2. Insert Data
3. View Data
4. Update Data
5. Delete Data
Enter Choice: 3 

1. View All
2. View as per mentioned key:value
Enter Choice: 1
123 123 123 123 123 {'model': '123', 'year': '123', 'value': '123'}
zhang san 123 456 6 {'model': '789', 'year': '2011', 'value': 'sss'}

