# -*- coding: utf-8 -*-

import requests, json

url="http://backend.yoisho.dob.jp/banking/v2/swagger"
url="http://backend.yoisho.dob.jp/fx/swagger"
swagger=requests.get(url).text
data=json.loads(swagger)
print (data["info"]["title"])
print (data["host"])
print (data["basePath"])
print (data["schemes"])

for p in data["paths"]:
    print ("PATH " + p)
    for m in data["paths"][p]:
        print (m)
