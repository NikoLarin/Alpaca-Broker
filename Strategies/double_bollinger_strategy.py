import pandas as pd
import time
from ta import add_all_ta_features
import requests
from ta.volatility import BollingerBands
from ta.utils import dropna
from alpaca_tools import get_ohlc, current_stock_price, headers

URL = "https://paper-api.alpaca.markets/v2/orders"

def bollinger_bands(t):    
    df = pd.DataFrame(get_ohlc('SPY','1Min'))
    df = df.rename(columns={  # names columns
                'o': 'Open',
                'h': 'High',
                'l': 'Low',
                'c': 'Close',
                't': 'Date'
            }
    )
    df = dropna(df)
    
    indicator_bb = BollingerBands(close=df["Close"], window=t, window_dev=2)

    # Add Bollinger Bands features
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()

    # Add Bollinger Band high indicator
    df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()

    # Add Bollinger Band low indicator
    df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()

    return df['bb_bbh'].iloc[-2], df['bb_bbm'].iloc[-2], df['bb_bbl'].iloc[-2]

trading = True


while trading == True:
    hour = time.localtime()
    while (hour[3] >= 9 and hour[4] >= 30)  or hour[3] < 16:
        
        t = [60, 15]
        bb = []
        for look_back in t:    
            bb.append(bollinger_bands(look_back))

        (bb_h_60, bb_m_60, bb_l_60) = bb[0]
        (bb_h_15, bb_m_15, bb_l_15) = bb[1]

        highband1 = bb_h_60
        highband2 = bb_h_15

        midband1 = bb_m_60

        lowband1 = bb_l_60
        lowband2 = bb_l_15

        price = current_stock_price('SPY')

        print(f'Upper: {highband1}\nPrice: {price}\nLower: {lowband1})')
        time.sleep(5)


        if price > highband1 and price > highband2:
            #short
            short = True
            payload = {
            "type": "market",
            "time_in_force": "day",
            "symbol": "SPY",
            "qty": "1",
            "side": "sell"
        }
            response = requests.post(URL, json=payload, headers=headers())
            print('ORDER SENT')
            while short == True:
                if price == midband1:
                    payload = {
                    "type": "market",
                    "time_in_force": "day",
                    "symbol": "SPY",
                    "qty": "1"
                }
                    response = requests.post(URL, json=payload, headers=headers())
                    short = False
                    print('FLATTEN ORDER SENT')
        
        elif price < lowband1 and price < lowband2:
            #long
            long = True
            payload = {
            "type": "market",
            "time_in_force": "day",
            "symbol": "SPY",
            "side": "buy",
            "qty": "1"
        }
            response = requests.post(URL, json=payload, headers=headers())
            print('ORDER SENT')
            while long == True:
                if price == midband1:
                    payload = {
                    "type": "market",
                    "time_in_force": "day",
                    "symbol": "SPY",
                    "qty": "1",
                    "side": "sell"
                }
                    response = requests.post(URL, json=payload, headers=headers())
                    long = False
                    print('FLATTEN ORDER SENT')
        else:
            time.sleep(60)
            continue



        
    
    print('Restarting loop: Searching for trade :)')
