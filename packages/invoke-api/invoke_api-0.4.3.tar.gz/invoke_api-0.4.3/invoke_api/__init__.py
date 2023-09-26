import logging

logger = logging.getLogger('hwapi')
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
lf = logging.Formatter(fmt='[%(asctime)s %(filename)s：%(lineno)d %(levelname)s] %(message)s', datefmt='%Y_%m_%d %H:%M:%S')
logger.addHandler(sh)
sh.setFormatter(lf)
