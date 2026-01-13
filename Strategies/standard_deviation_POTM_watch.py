from datetime import *; from dateutil.relativedelta import *
import calendar
import requests
from alpaca_tools import headers, get_ohlc, current_stock_price, options_chain
import time
import statistics
import math
from statistics import NormalDist

NOW = datetime.now()
EOM = NOW+relativedelta(day=31, weekday=FR(-1))
formatDate = list(EOM.timetuple())
#formatDate = (f'{formatDate[0]}{formatDate[1]:02}{formatDate[2]:02}')[2:]
dte = (EOM - NOW).days

fDate = []
fDate.append(datetime.year)


def snapshot(ticker,price):
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}?feed=opra&limit=1000&type=put&strike_price_lte={price}&expiration_date={f'{formatDate[0]}-{formatDate[1]:02d}-{formatDate[2]:02d}'}"
    response = requests.get(url, headers=headers())
    response = response.json()
    allCodes = sorted(response['snapshots'].keys())
    
    atm_option_code = allCodes[-1]
    
    atm_iv = response['snapshots'][atm_option_code]['impliedVolatility']

    sd = price * atm_iv * math.sqrt(dte/365)
    sdLevel = round(price-sd)
    
    closest_index = min(
    range(len(allCodes)),
    key=lambda i: abs((int(allCodes[i][-8:]) / 1000) - (sdLevel))
    )

    sd_strike_code = allCodes[closest_index]
    sd_strike_iv = response['snapshots'][sd_strike_code]['impliedVolatility']
    sd_strike_quote = response['snapshots'][sd_strike_code]['latestQuote']['ap']

    return [sdLevel, sd_strike_iv, sd_strike_quote]


def probITM(ticker, strike, iv, dte, price):
    S = price   # spot price
    K = strike                         # option strike
    sigma = iv                         # implied volatility
    T = dte / 365                      # time in years
    d2 = (math.log(S / K) - 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
    pitm = NormalDist().cdf(-d2)
    return pitm

TICKERS = [
'SPY','QQQ','IWM','DIA','GLD','IBIT','SLV','XLF','XLE','XLK','XLY',
 'XLI','XLP','XLV','XLB','XLU','SMH','XOP','KRE','FXI','EEM',
 'AAPL','MSFT','NVDA','AMZN','META','TSLA','GOOGL','GOOG','AMD','NFLX',
 'AVGO','TSM','ADBE','CRM','ORCL','CSCO','QCOM','INTC','MU','IBM',
 'JPM','BAC','WFC','GS','MS','C','V','MA','PYPL',
 'XOM','CVX','COP','SLB','OXY','BP','SHEL','EOG',
 'UNH','LLY','JNJ','MRK','ABBV','BMY','GILD','TMO','CVS',
 'WMT','HD','LOW','TGT','COST','MCD','SBUX','NKE','CMG','KO',
 'PEP','PG','CL','MO','PM','KMB','HSY',
 'CAT','DE','BA','GE','LMT','RTX','UPS','FDX','GM',
 'UBER','ABNB','SHOP','DIS','RIVN','F','LYFT','BABA','BIDU','TSLA'
 ]

for ticker in TICKERS:
    price = int(current_stock_price(ticker))
    data = snapshot(ticker, price)
    PITM = probITM(ticker, data[0], data[1], dte, price)
    ROR = round(data[2] / price * 100,2)
    print(f'{ticker} has {round(PITM * 100, 2)}% at {data[0]} and ROR: {ROR}%')


