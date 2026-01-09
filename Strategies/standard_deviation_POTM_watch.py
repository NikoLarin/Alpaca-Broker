from datetime import *; from dateutil.relativedelta import *
import calendar
import requests
from alpaca_tools import headers, get_ohlc, current_stock_price, options_chain
import time
import statistics
import math
from scipy.stats import norm


NOW = datetime.now()
EOM = NOW+relativedelta(day=31, weekday=FR(-1))
formatDate = list(EOM.timetuple())
formatDate = (f'{formatDate[0]}{formatDate[1]:02}{formatDate[2]:02}')[2:]
dte = (EOM - NOW).days

fDate = []
fDate.append(datetime.year)

def atm_option(ticker,capu):
    oCode = f'{ticker}{formatDate}{capu}{int(round(current_stock_price(ticker),0)):05d}000'
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots?symbols={oCode}&feed=opra&limit=1"
  
    response = requests.get(url, headers=headers())
    response = response.json()
    response = response['snapshots'][oCode]

    iv = response['impliedVolatility']
    delta = response['greeks']['delta']
    gamma = response['greeks']['gamma']
    theta = response['greeks']['theta']
    vega = response['greeks']['vega']
    quote = response['latestQuote']['ap']

    return iv

def find_sd(ticker,dte):
    sd = current_stock_price(ticker) * atm_option(ticker,capu='C') * math.sqrt(dte/365)
    sdLevels = [(current_stock_price(ticker)+sd), current_stock_price(ticker)-sd]
    print(sdLevels)


tickers = ['SPY', 'QQQ', 'NVDA']

for ticker in tickers:
    print(f'IV: {atm_option(ticker,'C')} For {ticker}')
    find_sd(ticker,dte)   
