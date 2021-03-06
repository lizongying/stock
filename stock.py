# -*- coding: utf-8 -*-
import datetime
import json
import time
from tkinter import messagebox, Label, Button, Entry, Tk, StringVar, ttk

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mpt
import matplotlib.ticker as mtick
import mpl_finance as mpf
import numpy
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn import linear_model
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

mpl.use('TkAgg')

s = requests.session()


def month():
    return str(datetime.date.today() - datetime.timedelta(30)).replace('-', '')


def half_year():
    return str(datetime.date.today() - datetime.timedelta(180)).replace('-', '')


def year():
    return str(datetime.date.today() - datetime.timedelta(360)).replace('-', '')


def all():
    return '19700101'


def get_csv(url):
    try:
        r = s.get(url)
        return r.text
    except:
        return False


def get_data():
    # 判断下请求数据的开始时间
    nu = number.get()
    if nu == '一个月':
        start = month()
    elif nu == '半年':
        start = half_year()
    elif nu == '一年':
        start = year()
    elif nu == '上市以来':
        start = all()
    else:
        return False

    # 获取股票名
    if not get_name():
        return False
    code = input_code.get().strip()
    end = str(datetime.datetime.now().date()).replace('-', '')
    url = 'http://quotes.money.163.com/hs/service/diyrank.php?query=SYMBOL%3A{code}'.format(code=code)
    r = s.get(url)
    code2 = json.loads(r.text)['list'][0]['CODE']
    url = 'http://quotes.money.163.com/service/chddata.html?code={code}&start={start}&end={end}&fields=TCLOSE;HIGH;LOW;TOPEN;VOTURNOVER'.format(
        code=code2, start=start, end=end)

    # 有失败的情况，加个重试机制
    retry = 0
    while retry < 3:
        retry += 1
        res = get_csv(url)
        if res:
            return res
    return False


def get_name():
    code = input_code.get().strip()
    if not code:
        messagebox.showinfo('提示', '无法获取该股票信息，请重新输入')
        return False
    url = 'http://quotes.money.163.com/stocksearch/json.do?count=10&word={code}'.format(code=code)
    r = s.get(url)
    try:
        name = json.loads(r.text[27:-1])[0]['name']
    except:
        messagebox.showinfo('提示', '无法获取该股票信息，请重新输入')
        return False
    root.title(name)
    return True


# 因为横坐标不是日期，需要把日期展示出来
def format_date(x, pos=None):
    # 对于超出范围的横坐标，返回个空
    if x < 0 or x > len(data_date) - 1:
        return ''
    return data_date[int(x)]


def draw():
    global data_date

    # 获取数据
    data = get_data()
    if not data:
        return
    date = input_date.get().strip()

    # 需要把数据转成一维数组，因为时间是反的，需要翻转一下，并把非数据的表头去掉
    data = list(filter(lambda i: i and len(i) > 1, reversed([i.split(',') for i in data.split('\n')])))[:-1]

    # 绘制图片的时候，只取k线图用到的数据
    data_stock = [[i, float(v[6]), float(v[4]), float(v[5]), float(v[3]), float(v[7])] for i, v in enumerate(data)]

    # 把日期提出来，后面展示日期的时候用到
    data_date = list([v[0] for v in data])

    # 成交量的数据提出来，并改为以万为单位，不然显示会太长而省略
    data_volume = [float(v[7]) / 10000 for v in data]

    # 提出测试数据，做校验分析的时候用到，样本比例为1/10，可根据情况修改
    x_train, x_test, y_train, y_test = train_test_split(
        numpy.array([time.mktime(time.strptime(v[0], '%Y-%m-%d')) for v in data]).reshape(-1, 1),
        [float(v[3]) for v in data], test_size=0.1, random_state=100)

    # 线性回归模型
    regr = linear_model.LinearRegression()
    regr.fit(x_train, y_train)

    # 预测填写的日期
    x_pred = numpy.array([time.mktime(time.strptime(i, '%Y%m%d')) for i in [date]]).reshape(-1, 1)
    y_pred = regr.predict(x_pred)
    Label(root, text='{predict}'.format(predict=round(y_pred[0], 2))).grid(row=0, column=5)
    y_pred = regr.predict(x_test)

    # 预测样本日期，并分析
    mse = numpy.sum([(y_pred[i] - y_test[i]) ** 2 for i in range(len(y_pred))]) / len(y_pred)
    rmse = numpy.sqrt(mse)
    mae = numpy.sum([abs(y_pred[i] - y_test[i]) for i in range(len(y_pred))]) / len(y_pred)
    r2 = r2_score(y_test, y_pred)
    fig.clf()
    ax = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4, facecolor='#07000d')

    # 画个k线
    mpf.candlestick_ohlc(ax, data_stock, width=0.6, colorup='r', colordown='g')

    # 预测下开始和结束时间，连起来
    x_pred = numpy.array([time.mktime(time.strptime(i, '%Y-%m-%d')) for i in [data_date[0], data_date[-1]]]).reshape(-1,
                                                                                                                     1)
    y_pred = regr.predict(x_pred)
    ax.plot([0, len(data_date) - 1], y_pred, 'b', label='Linear regression', linewidth=1.5)

    # 图例
    plt.legend(loc=0)
    ax.grid(True, color='w')

    # 横坐标最大展示间距，可以调整
    ax.xaxis.set_major_locator(mpt.MaxNLocator(10))
    ax.xaxis.set_major_formatter(mpt.FuncFormatter(format_date))
    ax.yaxis.label.set_color('w')
    ax.spines['bottom'].set_color('#5998ff')
    ax.spines['top'].set_color('#5998ff')
    ax.spines['left'].set_color('#5998ff')
    ax.spines['right'].set_color('#5998ff')
    ax.tick_params(axis='y', colors='w')
    plt.gca().yaxis.set_major_locator(mpt.MaxNLocator())
    plt.gcf().autofmt_xdate()
    ax.tick_params(axis='x', colors='w')
    plt.ylabel('Stock price and Volume')

    # 展示交易量
    ax1v = ax.twinx()
    ax1v.fill_between(range(len(data_stock)), data_volume, facecolor='#00ffe8', alpha=.4)
    ax1v.grid(False)
    ax1v.set_ylim(0, 2 * max(data_volume))
    fmt = '%dw'
    y_ticks = mtick.FormatStrFormatter(fmt)
    ax1v.yaxis.set_major_formatter(y_ticks)
    ax1v.spines['bottom'].set_color('#5998ff')
    ax1v.spines['top'].set_color('#5998ff')
    ax1v.spines['left'].set_color('#5998ff')
    ax1v.spines['right'].set_color('#5998ff')
    ax1v.tick_params(axis='x', colors='w')
    ax1v.tick_params(axis='y', colors='w')

    # 展示分析结果
    plt.table(cellText=[[round(mse, 2), round(rmse, 2), round(mae, 2), round(r2, 2)]],
              cellLoc='center',
              rowLabels=[''],
              colLabels=['MSE', 'RMSE', 'MAE', 'R Squared'],
              loc='top',
              )
    canvas.draw()


def _quit():
    root.quit()
    root.destroy()


def click():
    var.set(number.get())


if __name__ == '__main__':
    root = Tk()

    # 禁止最大化，如不对最大化处理，最大化后页面显示会很丑
    root.resizable(0, 0)
    root.title('股票')
    fig = plt.figure(facecolor='#07000d', figsize=(12, 8))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget()
    canvas._tkcanvas.grid(row=1, column=0, columnspan=9, rowspan=2, )
    Label(root, text='请输入股票代码：').grid(row=0, column=0)
    input_code = Entry(root)
    input_code.insert(0, '')
    input_code.grid(row=0, column=1)
    today = str(datetime.datetime.now().date()).replace('-', '')
    Label(root, text='请输入预测日期：').grid(row=0, column=2)
    input_date = Entry(root)
    input_date.insert(0, today)
    input_date.grid(row=0, column=3)
    Label(root, text='预测结果（收盘价）：').grid(row=0, column=4)
    Label(root, text='').grid(row=0, column=5)
    var = StringVar()
    label = Label(root, textvariable=var)
    label.grid(row=0, column=6)
    number = StringVar()
    numberChosen = ttk.Combobox(root, width=12, textvariable=number)
    numberChosen['values'] = ('一个月', '半年', '一年', '上市以来')
    numberChosen.grid(row=0, column=6)
    numberChosen.current(0)
    Button(root, text='开始', command=draw).grid(row=0, column=7)
    Button(master=root, text='退出', command=_quit).grid(row=0, column=8)
    root.mainloop()
