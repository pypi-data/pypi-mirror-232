# -*- coding: utf-8 -*-
import os


def get_root_dir() -> str:
    """
    获取项目运行路径
    :return:
    """
    root_dir = os.environ.get("root_dir")

    if not root_dir:
        root_dir = os.path.dirname(os.path.abspath(__file__))

        os.environ["root_dir"] = root_dir
