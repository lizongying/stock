# -*- coding: utf-8 -*-
import datetime
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
start = '19700101'
end = str(datetime.datetime.now().date()).replace('-', '')
url = 'http://quotes.money.163.com/hs/service/diyrank.php?query=SYMBOL%3A{code}'.format(code=code)
r = requests.get(url)
code2 = json.loads(r.text)['list'][0]['CODE']
url = 'http://quotes.money.163.com/service/chddata.html?code={code}&start={start}&end={end}&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'.format(
    code=code2, start=start, end=end)
r = requests.get(url)
with open('{code}.csv'.format(code=code), 'w') as f:
    f.write(r.text)
print('{code} 获取数据成功'.format(code=code))
