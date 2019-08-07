# -*- coding: utf-8 -*-
import time
from sys import argv

import numpy
import pandas
from matplotlib import pyplot
from sklearn import linear_model

try:
    r = int(argv[1])
    if not r:
        print('股票代码错误，请确认格式为"300270"')
except:
    print('股票代码错误，请确认格式为"300270"')
    exit()
try:
    r = int(argv[2])
    if not r:
        print('预测日期错误，请确认格式为"20190909"')
        exit()
except:
    print('预测日期错误，请确认格式为"20190909"')
    exit()
code = argv[1]
date = [argv[2]]
data_file = '{code}.csv'.format(code=code)
data = pandas.read_csv(data_file, encoding='gbk').sort_index(ascending=False)
regr = linear_model.LinearRegression()
regr.fit(numpy.array([time.mktime(time.strptime(i, '%Y-%m-%d')) for i in data['日期']]).reshape(-1, 1), data['收盘价'])
# print('coef: {coef}, intercept: {intercept}'.format(coef=regr.coef_, intercept=regr.intercept_))
xPred = numpy.array([time.mktime(time.strptime(i, '%Y%m%d')) for i in date]).reshape(-1, 1)
yPred = regr.predict(xPred)
# print('predict: {predict}'.format(predict=yPred))
print('预测结果为: {predict}（收盘价）'.format(predict=yPred[0]))
pyplot.scatter(data['日期'], data['收盘价'], color='blue')
pyplot.plot(data['日期'],
            regr.predict(numpy.array([time.mktime(time.strptime(i, '%Y-%m-%d')) for i in data['日期']]).reshape(-1, 1)),
            color='red', linewidth=4)
pyplot.show()
