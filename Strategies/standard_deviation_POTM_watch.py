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

from statistics import NormalDist
import math

def probITM(ticker, strike, iv, dte):
    S = current_stock_price(ticker)   # spot price
    K = strike                         # option strike
    sigma = iv                         # implied volatility
    T = dte / 365                      # time in years
    d2 = (math.log(S / K) - 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
    pitm = NormalDist().cdf(-d2)
    return pitm

def atm_option(ticker):
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}?feed=opra&limit=1&type=call&strike_price_gte={current_stock_price(ticker)}&expiration_date_gte={f'{formatDate[0]}-{formatDate[1]:02d}-{formatDate[2]:02d}'}"
    
    response = requests.get(url, headers=headers())
    response = response.json()

    return list(response['snapshots'].keys())


def option_data(ticker,capu):
    oCode = atm_option(ticker)
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots?symbols={oCode[0]}&feed=opra&limit=1"
  
    response = requests.get(url, headers=headers())
    response = response.json()
    response = response['snapshots'][oCode[0]]
    
    iv = response['impliedVolatility']
    delta = response['greeks']['delta']
    gamma = response['greeks']['gamma']
    theta = response['greeks']['theta']
    vega = response['greeks']['vega']
    quote = response['latestQuote']['ap']
    
    return iv

def find_sd(ticker,dte):
    sd = current_stock_price(ticker) * option_data(ticker,capu='P') * math.sqrt(dte/365)
    sdLevels = [(current_stock_price(ticker)+sd), current_stock_price(ticker)-sd]
    return sdLevels


tickers = ['AAPL','MSFT','NVDA','AMZN','META','TSLA','GOOGL','GOOG','JPM','V','MA',
 'UNH','LLY','XOM','AVGO','JNJ','PG','HD','CVX','MRK','PEP','ABBV','KO','COST',
 'BAC','WMT','CRM','ADBE','TMO','MCD','CSCO','ACN','ABT','LIN','DHR','TXN','NEE',
 'PM','WFC','MS','IBM','UNP','RTX','LOW','INTC','AMD','CAT','AMGN','SPGI','BLK',
 'NOW','MDT','SYK','ISRG','BKNG','LMT','DE','GS','GE','AMAT','ADI','MMC','GILD',
 'CB','AXP','REGN','PLD','CI','ELV','MO','T','VZ','SO','DUK','AEP','D','EXC',
 'SBUX','NKE','TGT','HD','LOW','ROST','TJX','DG','DLTR','BBY','ULTA','MAR','HLT',
 'BKNG','RCL','CCL','NCLH','DAL','UAL','AAL','LUV','UPS','FDX','NSC','CSX','CP',
 'PFE','MRNA','BMY','GILD','VRTX','BIIB','ZTS','IDXX','PANW','CRWD','ZS','NET','DDOG',
 'SNOW','MDB','PLTR','OKTA','TWLO','TEAM','PATH',
 'ORCL','SAP','INTU','SQ','PYPL','SHOP','UBER','LYFT','ABNB','ROKU','NFLX','DIS',
 'CMCSA','WBD','EA','TTWO','VZ','T','TMUS',
 'F','GM','TSLA','RIVN','LCID','TM','STLA','NIO','XPEV','LI','BA','LMT','NOC',
 'RTX','GD','HII','TDG','HEI','GE','HON','MMM','ETN','EMR','ROK','PH','AME','ITW',
 'COP','EOG','SLB','HAL','BKR','MPC','PSX','VLO','OXY','KMI','WMB','OKE',
 'META','GOOGL','GOOG','SNAP','PINS','BIDU','BABA','JD','PDD','NTES',
 'TSM','ASML','QCOM','MU','WDC','STX','KLAC','LRCX','AMAT','TER','COHR','QRVO',
 'C','BAC','WFC','MS','GS','JPM','USB','PNC','TFC','SCHW','BK','BLK','AIG','MET','PRU',
 'V','MA','AXP','DFS','COF','PYPL','SQ','FIS','FISV','GPN','ICE','CME','NDAQ','MSCI',
 'SPGI','MCO','CB','AON','AJG','TRV','ALL','PGR','WRB','CINF','HIG','L','MKL',
 'KO','PEP','MNST','KDP','KHC','GIS','K','CPB','SJM','HSY','MDLZ','CL','EL','PG','CHD',
 'WMT','TGT','COST','KR','ACI','WBA','CVS','AMZN','EBAY','ETSY','SHOP','HD','LOW',
 'NKE','LULU','UAA','VFC','PVH','RL','TAP','DEO','STZ','MO','PM','BTI',
 'SBUX','DNKN','CMG','QSR','YUM','MCD','WEN','DPZ','SHAK','DRI','CAKE','BJRI','TXRH']

for ticker in tickers:
    iv = option_data(ticker, 'P')
    strike = math.floor(find_sd(ticker,dte)[1])

    print(f'The PITM for {ticker} is {probITM(ticker,strike,iv,dte) * 100}% for the {strike} strike')



