import logging


# SingletonMeta是一个自定义的元类，在类_instances字典中存储已经创建的实例。当尝试创建一个MyLogger实例时，SingletonMeta的__call__方法会被触发
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# 使用SingletonMeta作为其元类的类，MyLogger是一个单例类
class MySingletonMeta(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, 'logger'):  # self是否没有名为logger的属性
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_info(self, message):
        self.logger.info(message)


if __name__ == '__main__':
    # 使用MyLogger类
    logger1 = MySingletonMeta()
    logger1.log_info("This is an info message from logger1")

    logger2 = MySingletonMeta()
    logger2.log_info("This is an info message from logger2")
