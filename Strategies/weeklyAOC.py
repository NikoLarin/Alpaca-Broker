'''
Calculates the weekly AOC then applies it to the tickers in the list [tickers]
if we are exceeding either side of the aoc an atm credit spread is sold


NEEDED UPDATES:
Add more tickers to the tickers list at the end.
Need to stop it from placing trades on repeat tickers.
'''
import requests
import time
import calendar
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from alpaca_tools import headers, current_stock_price, BASE_URL
from dateutil.relativedelta import *

TODAY = date.today()
FRIDAY = TODAY+relativedelta(weekday=FR)

dte = ''
dte_list = []

dte_list.append(FRIDAY.year)
dte_list.append(FRIDAY.month)
dte_list.append(FRIDAY.day)

for i in dte_list:
     dte += "{:02d}-".format(i)


def all_open_positions():
    url = "https://paper-api.alpaca.markets/v2/positions"

    response  = requests.get(url, headers=headers())
    data = response.json()

    
    return [position['symbol'] for position in data]



def aoc(ticker):
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={ticker}&timeframe=1W&start=2025-01-03&limit=8&adjustment=raw&feed=sip&sort=desc"

    response  = requests.get(url, headers=headers())
    data = response.json()

    bars = data["bars"][ticker]

    abs_pct_changes = []

    for candle in bars:
        closeD = candle["c"]
        openD = candle["o"]

        if openD != 0:
            abs_pct_changes.append(abs(((closeD - openD) / openD)))

    today_aoc = (sum(abs_pct_changes) / len(abs_pct_changes))
    weekly_open = data['bars'][ticker][0]["o"] 

    return [today_aoc, weekly_open] 

def call_spread(ticker, price,dte):
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}?feed=opra&limit=2&type=call&strike_price_gte={price}&expiration_date={dte}"

    response  = requests.get(url, headers=headers())
    data = response.json()

    return data

def put_spread(ticker, price,dte):
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}?feed=opra&limit=1000&type=put&strike_price_lte={price}&expiration_date={dte}"

    response  = requests.get(url, headers=headers())
    data = response.json()

    return data

TICKERS = [
'SPY','QQQ','IWM','DIA','GLD','IBIT','SLV','SMH','XOP','KRE','FXI','EEM',
 'AAPL','MSFT','NVDA','AMZN','META','TSLA','GOOGL','GOOG','AMD','NFLX',
 'AVGO','TSM','ADBE','CRM','ORCL','CSCO','QCOM','INTC','MU','IBM',
 'JPM','BAC','WFC','GS','MS','C','V','MA','PYPL','XOM',
 'UNH','LLY','JNJ','MRK','ABBV','BMY','GILD','TMO','CVS',
 'WMT','HD','LOW','TGT','COST','MCD','SBUX','NKE','CMG','KO','PEP','PG','CL','MO','PM','KMB','HSY',
 'CAT','DE','BA','GE','LMT','RTX','UPS','FDX','GM',
 'UBER','ABNB','SHOP','DIS','RIVN','F','LYFT','BABA','BIDU','TSLA','HOOD','MSTR',
 'PLTR','RBLX'
 ]
while True:
    all_positions = all_open_positions()
    for ticker in TICKERS:
        data = aoc(ticker)
        price = current_stock_price(ticker)
        weekly_open = data[1]
        waoc = data[0]

        highbar = weekly_open + (weekly_open * waoc)
        lowbar = weekly_open - (weekly_open * waoc)
        url = f'{BASE_URL}/orders'

        #----------for call spread----------#
        ocodes = list(call_spread(ticker,price,dte[:-1])['snapshots'].keys())
        
        if price > highbar and ocodes[0] not in all_positions:
                
            payload = { #creates the debit spread
                    "type": "market",
                    "time_in_force": "day",
                    "legs": [
                        {
                            "side": "buy",
                            "symbol": ocodes[1],
                            "ratio_qty": "1"
                        },
                        {
                            "side": "sell",
                            "symbol": ocodes[0],
                            "ratio_qty": "1"
                        }
                    ],
                    "order_class": "mleg",
                    "qty": "1"
                }
            response = requests.post(url, json=payload, headers=headers())
            TICKERS.remove(ticker)
            print(f'Order sent for {ticker}')
        #----------for put spread----------#
        elif price < lowbar and ocodes[-1] not in all_positions:
            ocodes = sorted(list(put_spread(ticker,price,dte[:-1])['snapshots'].keys()))
            payload = { #creates the debit spread
                "type": "market",
                "time_in_force": "day",
                "legs": [
                    {
                        "side": "buy",
                        "symbol": ocodes[-2],
                        "ratio_qty": "1"
                    },
                    {
                        "side": "sell",
                        "symbol": ocodes[-1],
                        "ratio_qty": "1"
                    }
                ],
                "order_class": "mleg",
                "qty": "1"
            }
            response = requests.post(url, json=payload, headers=headers())
            TICKERS.remove(ticker)
            print(f'Order sent for {ticker}')
        else:
            print(f'Highbar:{highbar}, Lowbar: {lowbar}, Ticker: {ticker}')
            continue
    time.sleep(30)


