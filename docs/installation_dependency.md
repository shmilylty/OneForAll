# 安装依赖

你可以通过pip3和pipenv两种方法安装OneForAll的依赖（熟悉哪种就用哪种）：

## Windows系统

注意：如果你的Python3安装在系统Program Files目录下，如：`C:\Program Files\Python38`，那么请以管理员身份运行命令提示符cmd执行以下命令！

1. 使用pipenv安装依赖
```bash
cd OneForAll/
python -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
pip3 install pipenv -i https://mirrors.aliyun.com/pypi/simple/
pipenv install --python 3.8
pipenv run python oneforall.py --help
```

2. 使用pip3安装依赖
```bash
cd OneForAll/
python -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python oneforall.py --help
```
## Linux系统

* **Ubuntu/Debian系统(包括kali)**
安装git
```bash
sudo apt update
sudo apt install git
```

克隆OneForAll项目
```bash
git clone https://gitee.com/shmilylty/OneForAll.git
```

安装python及开发依赖
```bash
sudo apt install python3.8 python3.8-dev python3-testresources
```
接下来你可以使用以下一种方式安装OneForAll的Python库依赖:
1. 使用pipenv安装依赖
```bash
cd OneForAll/
sudo python3.8 -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
sudo apt install pipenv
sudo pipenv install --python 3.8
pipenv run python3 oneforall.py --help
```

2. 使用pip3安装依赖
```bash
cd OneForAll/
sudo apt install python3-pip
sudo python3.8 -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
sudo pip3 install uvloop -i https://mirrors.aliyun.com/pypi/simple/
sudo pip3 install --ignore-installed -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python3.8 oneforall.py --help
```
## Darwin系统

1. 使用pipenv安装依赖
```bash
cd OneForAll/
python3 -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
pip3 install pipenv -i https://mirrors.aliyun.com/pypi/simple/
pipenv install --python 3.8
pipenv run python3 oneforall.py --help
```

2. 使用pip3安装依赖
```bash
cd OneForAll/
python3 -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
pip3 install uvloop -i https://mirrors.aliyun.com/pypi/simple/
python3 oneforall.py --help
```
