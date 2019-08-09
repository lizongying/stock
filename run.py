# -*- coding: utf-8 -*-

import subprocess
import time
code = input('请输入股票代码（如300270）：')
print('您输入的股票代码是：{code}'.format(code=code))
command = 'python search.py {code}'.format(code=code)
subprocess.Popen(command)
time.sleep(1)
date = input('请输入预测日期（如20190909）：')
print('您输入的预测日期是：{date}'.format(date=date))
command = 'python data.py {code}'.format(code=code)
subprocess.Popen(command)
time.sleep(5)
command = 'python analysis.py {code} {date}'.format(code=code, date=date)
subprocess.Popen(command)
