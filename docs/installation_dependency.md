# 安装依赖

你可以通过pip3和pipenv两种方法安装OneForAll的依赖（如果你熟悉[pipenv](https://docs.pipenv.org/en/latest/)，那么推荐使用你使用pipenv）：

* **Windows系统**（注意：如果你的Python3安装在系统Program Files目录下，如：`C:\Program Files\Python38`，那么请以管理员身份运行命令提示符cmd执行以下命令！）

    1. 使用pipenv

    ```bash
    cd OneForAll/
    python -m pip install --user -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
    pip3 install --user pipenv -i https://mirrors.aliyun.com/pypi/simple/
    pipenv install --user --python 3.8
    cd oneforall
    pipenv run python oneforall.py --help
    ```

    2. 使用pip3

    ```bash
    cd OneForAll/
    python -m pip install --user  -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
    pip3 install --user -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    cd oneforall/
    python oneforall.py --help
    ```
* **Linux系统**

    1. 使用pipenv
    ```bash
    cd OneForAll/
    python3 -m pip install --user -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
    sudo pip3 install --user pipenv -i https://mirrors.aliyun.com/pypi/simple/
    sudo pipenv install --user --python 3.8
    cd oneforall
    pipenv run python3 oneforall.py --help
    ```
    2. 使用pip3
    ```bash
    cd OneForAll/
    python3 -m pip install --user -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
    pip3 install --user -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    cd oneforall/
    python3 oneforall.py --help
    ```
* **Darwin系统**

    1. 使用pipenv
    ```bash
    cd OneForAll/
    python3 -m pip install --user -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
    pip3 install --user pipenv -i https://mirrors.aliyun.com/pypi/simple/
    pipenv install --user --python 3.8
    cd oneforall
    pipenv run python3 oneforall.py --help
    ```
    2. 使用pip3
    ```bash
    cd OneForAll/
    python3 -m pip install --user -U pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/
    pip3 install --user -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    cd oneforall/
    python3 oneforall.py --help
    ```