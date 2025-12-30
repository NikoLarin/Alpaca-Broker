import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://paper-api.alpaca.markets/v2"

def headers():
    return {
        "accept": "application/json",
        "APCA-API-KEY-ID": 'YOUR API KEY',
        "APCA-API-SECRET-KEY": 'YOUR API KEY',
    }

def accountValue():
    response = requests.get(f'{BASE_URL}/account', headers=headers()) # calls headers
    response = response.json()
    
    return response['portfolio_value']

def stockPrice(sym):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/snapshot"

    response = requests.get(url, headers=headers()) #calls headers function
    response = response.json()

    return response['dailyBar']['c']
        
def pctDailyChange(sym):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/snapshot"

    response = requests.get(url, headers=headers()) #calls headers function
    response = response.json()
    
    openPrice = response['prevDailyBar']['c'] #Daily bar open 
    closePrice = response['dailyBar']['c'] #latest price    
    
    pctChange = round(((closePrice - openPrice) / openPrice), 4) * 100

    return pctChange

def get_open_positions(): # return all open positions
    response = requests.get(f'{BASE_URL}/positions', headers=headers()) # calls headers
    response = response.json()
    
    return response['positions'] # all open positions

def is_market_open():
    response = requests.get(f'{BASE_URL}/clock', headers=headers()) # calls headers
    response = response.json()

    return response['is_open'] #returns bool if mkt open/closed

def option(ticker, oCode): #needs symbol and option code
    response = requests.get(f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}?feed=opra&limit=100&root_symbol={oCode}", headers=headers()) # gets live option based on oCode
    response = response.json()

    snap = response["snapshots"][oCode]

    greeks = response['greeks']
    impliedVolatility = snap['impliedVolatility'] 
    price = snap['latestQuote']['ap']

    return (greeks, impliedVolatility, price) # returnts a tuple

def options_chain():
    #implement a simple filter to only get the most recent x strikes
    response = requests.get(f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}")
    response = response.json()

    return response['snapshots'] # returns huge chain

def position_history():
    pass

def chart():
    pass

