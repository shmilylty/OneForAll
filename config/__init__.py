import importlib
from config import default


class Settings(object):
    def __init__(self):
        # 获取全局变量中的配置信息
        for attr in dir(default):
            setattr(self, attr, getattr(default, attr))

        setting = importlib.import_module('config.setting')

        for attr in dir(setting):
            setattr(self, attr, getattr(setting, attr))


settings = Settings()
