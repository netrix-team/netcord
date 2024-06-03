import logging

msg_fmt = '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] :: %(message)s'  # noqa: E501
logging.basicConfig(level=logging.INFO, format=msg_fmt, datefmt='%d.%m.%Y %H:%M:%S')  # noqa: E501


def get_logger(name):
    return logging.getLogger(name)
