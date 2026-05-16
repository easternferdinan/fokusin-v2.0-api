import logging

logger = logging.getLogger("app")

logger.setLevel(logging.INFO)

handler = logging.StreamHandler()

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler.setFormatter(formatter)

logger.addHandler(handler)

logger.propagate = False