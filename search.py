# -*- coding: utf-8 -*-
import json
from sys import argv

import requests

try:
    r = int(argv[1])
    if not r:
        print('股票代码错误，请确认格式为"300270"')
except:
    print('股票代码错误，请确认格式为"300270"')
    exit()
code = argv[1]
url = 'http://quotes.money.163.com/stocksearch/json.do?count=10&word={code}'.format(code=code)
r = requests.get(url)
print(json.dumps(json.loads(r.text[27:-1]), indent=2, ensure_ascii=False))
