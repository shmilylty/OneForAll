# 安装依赖

## Windows系统

注意：如果你的Python3安装在系统Program Files目录下，如：`C:\Program Files\Python38`，那么请以管理员身份运行命令提示符cmd执行以下命令！

```bash
cd OneForAll/
python -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python oneforall.py --help
```

## Linux系统

### Ubuntu/Debian系统(包括kali)

1. 安装git和pip3
```bash
sudo apt update
sudo apt install git python3-pip -y
```

2. 克隆OneForAll项目
```bash
git clone https://gitee.com/shmilylty/OneForAll.git
```

3. 安装相关依赖
```bash
cd OneForAll/
sudo apt install python3-dev python3-pip python3-testresources -y
sudo python3 -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
sudo pip3 install --ignore-installed -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python3 oneforall.py --help
```

### RHEL/Centos系统

1. 安装git和pip3
```bash
sudo yum update
sudo yum install git python3-pip -y
```

2. 克隆OneForAll项目
```bash
git clone https://gitee.com/shmilylty/OneForAll.git
```

3. 安装相关依赖
```bash
cd OneForAll/
sudo yum install gcc python3-devel python3-pip -y
sudo python3 -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
sudo pip3 install --ignore-installed -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python3 oneforall.py --help
```

## Darwin系统

克隆OneForAll项目
```bash
git clone https://gitee.com/shmilylty/OneForAll.git
```

安装相关依赖
```bash
cd OneForAll/
python3 -m pip install -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python3 oneforall.py --help
```
