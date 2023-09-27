# -*- coding: UTF-8 -*-
# @Time : 2023/9/26 18:34 
# @Author : 刘洪波
import yaml


def load_yaml(file_path: str): return yaml.safe_load(open(file_path, 'r', encoding="utf-8"))