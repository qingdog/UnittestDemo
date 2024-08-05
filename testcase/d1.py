from loguru import logger


def func(a: int, b: int):
    a/b


try:
    func(0, 0)
except Exception as error:
    # logger.exception(error)
    logger.error(error)