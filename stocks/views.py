from django.shortcuts import render, redirect
from django.http import HttpResponse
from urllib.request import Request, urlopen
import time
import json
import matplotlib.pyplot as plt
# Create your views here.
import pandas as pd
# from finlab.backtest import backtest
from finlab.data import Data
import datetime
# from finlab.backtest import portfolio
from cmoney import CmoneyVirtualStock
import warnings
from django.http import JsonResponse
warnings.simplefilter(action='ignore', category=FutureWarning)


def toSeasonal(df):
    season4 = df[df.index.month == 3]
    season1 = df[df.index.month == 5]
    season2 = df[df.index.month == 8]
    season3 = df[df.index.month == 11]

    season1.index = season1.index.year
    season2.index = season2.index.year
    season3.index = season3.index.year
    season4.index = season4.index.year - 1

    newseason1 = season1
    newseason2 = season2 - season1.reindex_like(season2)
    newseason3 = season3 - season2.reindex_like(season3)
    newseason4 = season4 - season3.reindex_like(season4)

    newseason1.index = pd.to_datetime(newseason1.index.astype(str) + '-05-15')
    newseason2.index = pd.to_datetime(newseason2.index.astype(str) + '-08-14')
    newseason3.index = pd.to_datetime(newseason3.index.astype(str) + '-11-14')
    newseason4.index = pd.to_datetime((newseason4.index + 1).astype(str) + '-03-31')

    return newseason1.append(newseason2).append(newseason3).append(newseason4).sort_index()


def get_stocks(request):
    return render(request,'stocks.html')

def post_stocks(request):
    Test = 1e10
   

    # ---------------------策略參數------------------
    values = float(request.POST['values'])
    freecashflow = float(request.POST['freecashflow'])
    shareholder = float(request.POST['shareholder'])
    grows = float(request.POST['grows'])
    Revenue = float(request.POST['Revenue'])
    rsvs = float(request.POST['rsvs'])
    pricess = float(request.POST['pricess'])    
    # -----------------------參數---------------------
    data = Data()
    Sda = request.POST['startdate'].split('-')
    start_date = datetime.date(int(Sda[0]),int(Sda[1]),int(Sda[2]))
    ends = request.POST['enddate'].split('-')
    end_date = datetime.date(int(ends[0]),int(ends[1]),int(ends[2]))
    strategy = mystrategy2
    data = data
    hold_days = int(request.POST['Tperiod'])
    stocks = mystrategy2(data,values,freecashflow,shareholder,grows,Revenue,rsvs,pricess)
    weight='average'
    benchmark=None
    stop_loss=None
    stop_profit=None
    # ------------------------參數---------------------
    SD = []
    ED = []
    NS = []
    Returns = []
    

    # portfolio check
    if weight != 'average' and weight != 'price':
        print('Backtest stop, weight should be "average" or "price", find', weight, 'instead')

    # get price data in order backtest
    data.date = end_date
    price = data.get('收盤價', (end_date - start_date).days)
    # start from 1 TWD at start_date, 
    end = 1
    date = start_date
    
    # record some history
    equality = pd.Series()
    nstock = {}
    transections = pd.DataFrame()
    maxreturn = -10000
    minreturn = 10000

    
    def date_iter_periodicity(start_date, end_date, hold_days):
        date = start_date
        while date < end_date:
            yield date, date + datetime.timedelta(hold_days)
            date += datetime.timedelta(hold_days)



    def date_iter_specify_dates(start_date, end_date, hold_days):
        dlist = [start_date] + hold_days + [end_date]
        if dlist[0] == dlist[1]:
            dlist = dlist[1:]
        if dlist[-1] == dlist[-2]:
            dlist = dlist[:-1]
        for sdate, edate in zip(dlist, dlist[1:]):
            yield sdate, edate
    
    if isinstance(hold_days, int):
        dates = date_iter_periodicity(start_date, end_date, hold_days)
    elif isinstance(hold_days, list):
        dates = date_iter_specify_dates(start_date, end_date, hold_days)
    else:
        print('the type of hold_dates should be list or int.')
        return None
    
    

   
    

    for sdate, edate in dates:
        
       
        
        # select stocks at date
        data.date = sdate
        stocks = strategy(data,values,freecashflow,shareholder,grows,Revenue,rsvs,pricess)
        ST= []
        ST.append(stocks.index)
        
        # hold the stocks for hold_days day
        s = price[stocks.index][sdate:edate].iloc[1:]
        
        
        if s.empty:
            s = pd.Series(1, index=pd.date_range(sdate + datetime.timedelta(days=1), edate))
        else:
            
            if stop_loss != None:
                below_stop = ((s / s.bfill().iloc[0]) - 1)*100 < -np.abs(stop_loss)
                below_stop = (below_stop.cumsum() > 0).shift(2).fillna(False)
                s[below_stop] = np.nan
                
            if stop_profit != None:
                above_stop = ((s / s.bfill().iloc[0]) - 1)*100 > np.abs(stop_profit)
                above_stop = (above_stop.cumsum() > 0).shift(2).fillna(False)
                s[above_stop] = np.nan
                
            s.dropna(axis=1, how='all', inplace=True)
            
            # record transections
            transections = transections.append(pd.DataFrame({
                'buy_price': s.bfill().iloc[0],
                'sell_price': s.apply(lambda s:s.dropna().iloc[-1]),
                'lowest_price': s.min(),
                'highest_price': s.max(),
                'buy_date': pd.Series(s.index[0], index=s.columns),
                'sell_date': s.apply(lambda s:s.dropna().index[-1]),
            }))
            
            transections['profit(%)'] = (transections['sell_price'] / transections['buy_price'] - 1) * 100
            
            s.ffill(inplace=True)
                
            # calculate equality
            # normalize and average the price of each stocks
            if weight == 'average':
                s = s/s.bfill().iloc[0]
            s = s.mean(axis=1)
            s = s / s.bfill()[0]
        
        

        # print some log
     
        SD.append(sdate)
        ED.append(edate)
        Returns.append(round(( s.iloc[-1]/s.iloc[0] * 100 - 100),2))
        NS.append(len(stocks))
        
        
        # print(SD)
        # print(ED)
        # print(Returns)

        print( sdate,'-', edate, 
            '報酬率: %.2f'%( s.iloc[-1]/s.iloc[0] * 100 - 100), 
            '%', 'nstock', len(stocks))
        maxreturn = round(max(maxreturn, s.iloc[-1]/s.iloc[0] * 100 - 100),2)
        minreturn = round(min(minreturn, s.iloc[-1]/s.iloc[0] * 100 - 100),2)


        # plot backtest result
        ((s*end-1)*100).plot()
        equality = equality.append(s*end)
        end = (s/s[0]*end).iloc[-1]
        
        # add nstock history
        nstock[sdate] = len(stocks)

    print('每次換手最大報酬 : %.2f ％' % maxreturn)
    print('每次換手最少報酬 : %.2f ％' % minreturn)
    S =  str(print('每次換手最少報酬 : %.2f ％' % minreturn))
 

    if benchmark == None:
        benchmark = price['0050'][start_date:end_date].iloc[1:]
    
    # # bechmark (thanks to Markk1227)
    Test = ((benchmark/benchmark[0]-1)*100)
    ((benchmark/benchmark[0]-1)*100).plot(color=(0.8,0.8,0.8))
    plt.ylabel('Return On Investment (%)')
    plt.grid(linestyle='-.')
    # # plt.show()
    # ((benchmark/benchmark.cummax()-1)*100).plot(legend=True, color=(0.8,0.8,0.8))
    # ((equality/equality.cummax()-1)*100).plot(legend=True)
    # plt.ylabel('Dropdown (%)')
    # plt.grid(linestyle='-.')
    # plt.show()
    # pd.Series(nstock).plot.bar()
    # plt.ylabel('Number of stocks held')


    ToHTML = zip(SD, ED, Returns,NS)
    Rmax = str('每次換手最大報酬 : ' )
    Rmin = str('每次換手最小報酬 : ' )
    pa = str('%')
    recoment = str('建議股票為: ')
    STT = ST[0]
    print(ST)
    print(stocks)

    list = ['view', 'Json', 'JS']
    x = [1, 2, 3, 4, 5, 6, 10]
    y = [0.125, 0.25, 0.5, 1, 2, 4, 30]
    Test = 'Test~!!!!'
    print(benchmark)
    print(type(benchmark))
    # print(benchmark.date)
    # print(benchmark.loc[[0]])
    print(benchmark.index[0])
    print(benchmark.iloc[0])

    z = []
    g = []
    Tw50 = []

    for k in benchmark.index:
        z.append(str(k))
    OR = benchmark[0]

    for k in benchmark.data:
        Tw50.append(((k/OR-1)*100))

    CUM = ((equality/equality.cummax()-1)*100)
    for k in CUM.data:
         g.append(k)

    equal = (equality - 1)*100
    returntest = []
    for k in equal.data:
        returntest.append(k)

    print(z)
    print(g)

    return render(request,'stocks.html',{
            'List': json.dumps(list),
            'x': json.dumps(z),
            'y': json.dumps(returntest),
            'Tw50' : json.dumps(Tw50),
            'returntest' : json.dumps(returntest),
            'STT': STT, 
            'recoment': '建議股票為: ', 
            'pa': '%', 
            'Rmin': '每次換手最小報酬 : ', 
            'Rmax': '每次換手最大報酬 : ', 
            'maxreturn': maxreturn,
            'minreturn': minreturn,
            'ToHTML': ToHTML, 
            'S': S, 
            's': s, 
            'ST': ST, 
            'edate': edate, 
            'sdate': sdate,
            'dates':dates, 
            'nstock': nstock, 
            'date': date, 
            'end': end, 
            'price': price, 
            'Returns': Returns, 
            'NS': NS, 
            'ED': ED, 
            'SD': SD, 'stop_profit': None, 'stop_loss': None, 
            'benchmark': benchmark,
            'stocks': stocks, 
            'hold_days': hold_days, 
            'strategy': strategy, 
            'end_date': end_date, 
            'ends': ends, 
            'start_date': start_date, 
            'Sda': Sda,
            'Test' : Test,
            'rsvs' : rsvs })


def get_add(request):
    # response = request.get('http://127.0.0.1:8000/add/api')
    # test = response.json()

    return render(request,'test.html')

def post_add(request,response):
    A = int(request.POST['A'])
    B = int(request.POST['B'])
    print ("Post")
    response
    test = get_add_api(request,A,B)
    return render(request,'test.html')

def get_add_api(request,A,B):
    A = int(request.POST['A'])
    B = int(request.POST['B'])
    result =  A + B
    print ("API")
    print (result)
   

    return JsonResponse({
            # 'List':list,
            'result' : result,
                })



def mystrategy2(data,values,freecashflow,shareholder,grows,Revenue,rsvs,pricess): 
    
    股本 = data.get('股本合計', 1)#.drop_duplicates(['stock_id', 'date'], keep='last')#.pivot(index='date', columns='stock_id')
    price = data.get('收盤價', 200)
    當天股價 = price[:股本.index[-1]].iloc[-1]
    當天股本 = 股本.iloc[-1]
    市值 = 當天股本 * 當天股價 / 10 * 1000
   

    df1 = toSeasonal(data.get('投資活動之淨現金流入（流出）', 5))
    df2 = toSeasonal(data.get('營業活動之淨現金流入（流出）', 5))
    自由現金流 = (df1 + df2).iloc[-4:].mean()
    
    
    稅後淨利 = data.get('本期淨利（淨損）', 1)
    
    # 股東權益，有兩個名稱，有些公司叫做權益總計，有些叫做權益總額
    # 所以得把它們抓出來
    權益總計 = data.get('權益總計', 1)
    權益總額 = data.get('權益總額', 1)
    
    # 並且把它們合併起來
    權益總計.fillna(權益總額, inplace=True)
        
    股東權益報酬率 = 稅後淨利.iloc[-1] / 權益總計.iloc[-1]
    
    
    營業利益 = data.get('營業利益（損失）', 5)
    營業利益成長率 = (營業利益.iloc[-1] / 營業利益.iloc[-5] - 1) * 100
    
    
    當月營收 = data.get('當月營收', 4) * 1000
    當季營收 = 當月營收.iloc[-4:].sum()
    市值營收比 = 市值 / 當季營收

    rsv = (price.iloc[-1] - price.iloc[-150:].min()) / (price.iloc[-150:].max() - price.iloc[-150:].min())
    
    
    condition1 = (市值 < values )
    condition2 = 自由現金流 > freecashflow
    condition3 = 股東權益報酬率 > shareholder
    condition4 = 營業利益成長率 > grows
    condition5 = 市值營收比 < Revenue
    condition6 = rsv > rsvs 
    condition7 = price.iloc[-1] < pricess

    select_stock = condition1 & condition2 & condition3 & condition4 & condition5 & condition6 & condition7
    
    return select_stock[select_stock]


# def updata():
        # 每日固定時間更新data
#     import datetime
#     from finlab.crawler import update_table

#     update_table(conn, 'price', crawl_price, [datetime.date(2018,12,11)])
#     update_table(conn, 'monthly_revenue', crawl_monthly_report, [datetime.date(2018,12,11)])
#     update_table(conn, 'finance_statement', crawl_finance_statement_by_date, [datetime.date(2018,12,11)])



def get_plot(request):
    # list =  ['view', 'Json', 'JS']
    # x = [1, 2, 3, 4, 5, 6, 10]
    # y = [0.125, 0.25, 0.5, 1, 2, 4, 30]
    # Test = str("Test!!!!")
    # print (Test)
    # print(locals())
    return render(request, 'plot.html')
    
    # ,{
    #         'List': json.dumps(list),
    #         'x': json.dumps(x),
    #         'y': json.dumps(y),
    #         'Test' : Test ,
    #             })




def get_plot_api(request):
    list =  ['view', 'Json', 'JS']
    x = [1, 2, 3, 4, 5, 6, 10 , 40, 50]
    y = [0.125, 0.25, 0.5, 1, 2, 4, 30,60,100]
    Test = str("Test!!!!")
    print (Test)
    print(locals())
    T = locals()
    


    return JsonResponse({
            # 'List':list,
            'x': x,
            'y': y,
            'Test' : Test,
                })                