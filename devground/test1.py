# -*- coding: utf-8 -*-
import yaml
import io

with open("ATM_Locations-5490.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

print(data_loaded)
