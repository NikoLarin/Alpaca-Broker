import requests
import time
import calendar
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from alpaca_tools import headers, open_stock_price, current_stock_price, aoc, BASE_URL
from dateutil.relativedelta import *

TODAY = date.today()
FRIDAY = TODAY+relativedelta(weekday=FR)

emptystring = ''
emptylist = []

emptylist.append(FRIDAY.year)
emptylist.append(FRIDAY.month)
emptylist.append(FRIDAY.day)

for i in emptylist:
     emptystring += "{:02d}".format(i)

def aoc(ticker):
    '''
    this function pulls open and close data for 100 days and calculates the 
    average open to close change for one day   
    '''

    
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={ticker}&timeframe=1W&start=2024-01-03&limit=8&adjustment=raw&feed=sip&sort=desc"

    response  = requests.get(url, headers=headers())
    data = response.json()

    bars = data["bars"][ticker]

    abs_pct_changes = []

    for candle in bars:
        closeD = candle["c"]
        openD = candle["o"]

        if openD != 0:
            abs_pct_changes.append(abs(((closeD - openD) / openD)))

    today_aoc = sum(abs_pct_changes) / len(abs_pct_changes)

    return today_aoc

def aoc_strategy(ticker):
        
        while True:    
                hour = time.localtime() # current time
                while hour[3] > 9 or hour[3] < 16:
                    for t in ticker:   
                        today_aoc = aoc(t)
                        stock_price = current_stock_price(t)
                        
                        today = str(date.today())
                        today = today.replace('-', '')

                        today_open = open_stock_price(t)
                        highbar = today_open + today_open * today_aoc
                        lowbar =  today_open - today_open * today_aoc

                        if stock_price > highbar: # if price is higher than top AOC
                            otype = 'C'
                            strike = round(stock_price, 0)
                            long_leg = f'{t}{emptystring[2:]}{otype}00{int(strike + 1)}000'
                        
                        elif stock_price < lowbar: #if price is lower than bottom AOC
                            otype = 'P'
                            strike = round(stock_price, 0)
                            long_leg = f'{t}{emptystring[2:]}{otype}00{int(strike - 1)}000'
                        
                        else:
                            print(f'Highbar:{highbar} Lowbar: {lowbar}')
                            print("Waiting")
                            time.sleep(10)
                            continue
                        
                        short_leg = f'{t}{emptystring[2:]}{otype}00{int(strike)}000'
                        
                        url = f'{BASE_URL}/orders'

                        payload = { #creates the debit spread
                            "type": "market",
                            "time_in_force": "day",
                            "legs": [
                                {
                                    "side": "buy",
                                    "symbol": long_leg,
                                    "ratio_qty": "1"
                                },
                                {
                                    "side": "sell",
                                    "symbol": short_leg,
                                    "ratio_qty": "1"
                                }
                            ],
                            "order_class": "mleg",
                            "qty": "1"
                        }
                        
                        response = requests.post(url, json=payload, headers=headers())
                        print(response.text)
                        ticker.remove(t) #this will only take one trade per day for each ticker
                        break
                    


ticker = ['SPY', 'QQQ', 'AMD', 'NVDA', 'WMT', 'RBLX', 'IBIT']

print(aoc_strategy(ticker))



