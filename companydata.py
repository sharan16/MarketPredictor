import bs4 as bs
import os
import pickle
import requests
import pandas_datareader.data as web
import datetime as dt
import pandas as pd

def save_tkrs():
    if not os.path.isfile('sp500tkrs.pkl'):
        response = requests.get("https://www.slickcharts.com/sp500")
        soup = bs.BeautifulSoup(response.text,"lxml")
        table = soup.find('table', {'class' : 'table table-hover table-borderless table-sm'})
        tkrs = []
        for row in table.findAll('tr')[1:]:
            tkr = row.findAll('td')[2].text
            tkrs.append(tkr)
        with open("sp500tkrs.pkl","wb") as f:
            pickle.dump(tkrs,f)
    else:
        with open("sp500tkrs.pkl","rb") as f:
            tkrs = pickle.load(f)
    return tkrs

def get_data_yahoo(reload_sp500 = False):
    if reload_sp500:
        tkrs = save_tkrs()
    else:
        with open("sp500tkrs.pkl","rb") as f:
            tkrs = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    start = dt.datetime(2000,1,1)
    end = dt.datetime(2016,12,31)
    for tkr in tkrs[0:20]:
        print(tkr)
        if not os.path.exists('stock_dfs/{}.csv'.format(tkr)):
            df = web.DataReader(tkr.replace('.','-'),'yahoo',start)
            df.to_csv('stock_dfs/{}.csv'.format(tkr))
        else:
            print('Already have {}.csv'.format(tkr))
def compile_data():
    with open("sp500tkrs.pkl",'rb') as f:
        tkrs = pickle.load(f)
    main_df =pd.DataFrame()
    for count,tkr in enumerate(tkrs):
        if os.path.exists('stock_dfs/{}.csv'.format(tkr)):
            df = pd.read_csv('stock_dfs/{}.csv'.format(tkr))
            df.set_index('Date',inplace = True)
            df.rename(columns = {'Adj Close': tkr}, inplace = True)
            df.drop(['Open','High','Low','Close','Volume'],1, inplace= True)
            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how = 'outer')
            #print(main_df.head())
            main_df.to_csv('SP500data.csv')

compile_data()
