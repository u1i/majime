# -*- coding: utf-8 -*-
import yaml
import io

with open("t1.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

print(data_loaded)
