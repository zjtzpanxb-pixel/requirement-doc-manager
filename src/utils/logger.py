"""日志工具"""

import logging
import sys
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
