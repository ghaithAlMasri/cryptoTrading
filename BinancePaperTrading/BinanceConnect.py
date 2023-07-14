import pandas as pd
from binance import Client
import numpy as np
import json
from datetime import datetime as dt
import math



class BinanceLive:
    def __init__(self, client_id, client_secret, duration, timeframe:str, symbol) -> None:

        self.client_id = client_id
        self.client_secret = client_secret
        self.client = Client(client_id, client_secret)
        self.df = pd.DataFrame()
        self.symbol = symbol
        self.entry_amount = None

        if timeframe.lower() == 'hourly':
            self.get_klines_hourly(self.symbol, duration)
        elif timeframe.lower() == 'minutes':
            self.get_klines_30_minutes(self.symbol, duration)


    def get_balance(self):
        acc_balance = pd.DataFrame(self.client.futures_account_balance())
        busd_balance = float(acc_balance[acc_balance['asset'] == 'BUSD']['balance'])
        return busd_balance


    def get_klines_hourly(self, symbol, duration):
        klines = pd.DataFrame(self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, duration))
        klines.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close time', 'quote asset volume', 'number of trades', 'taker buy base asset volume', 'taker buy quote asset volume', 'ignore']
        klines.set_index('time')
        klines = klines.iloc[:, :6]
        klines = klines.astype(float)
        klines.time = klines.time / 1000
        klines.time = [dt.utcfromtimestamp(date) for date in klines.time]
        self.df = klines

    def get_klines_30_minutes(self,symbol, duration):
        klines = pd.DataFrame(self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_30MINUTE, duration))
        klines.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close time', 'quote asset volume', 'number of trades', 'taker buy base asset volume', 'taker buy quote asset volume', 'ignore']
        klines.set_index('time')
        klines = klines.iloc[:, :6]
        klines = klines.astype(float)
        klines.time = klines.time / 1000
        klines.time = [dt.utcfromtimestamp(date) for date in klines.time]
        self.df = klines

    def get_last_price(self):
        last_price = self.df.close.values[-1]
        return last_price
    
    def get_precision(self):
        symbol_info = self.client.futures_exchange_info()
        symbol_precision = None
        for pair in symbol_info['symbols']:
            if pair['symbol'] == self.symbol:
                symbol_precision = pair['quantityPrecision']
                break

        if symbol_precision is None:
            raise Exception("Symbol precision not found.")
        
        return symbol_precision
    
    def market_order(self, direction: str):
        if direction.lower() == "long":
            side = "BUY"
        elif direction.lower() == "short":
            side = "SELL"
        else:
            raise Exception("Direction must be 'long' or 'short'.")


        symbol_precision = self.get_precision()

        amount = float(self.get_balance()) / float(self.get_last_price())


        amount = round(amount, symbol_precision)


        

        the_order = self.client.futures_create_order(
            symbol=self.symbol,
            side=side,
            quantity=amount,
            type='MARKET'
        )


        return the_order
    
    def get_open_positions(self):
        positions = self.client.futures_position_information()
        open_positions = []

        for position in positions:
            if float(position['positionAmt']) != 0:
                open_positions.append(position)
        return open_positions
    

    def set_open_position_amount(self):
        amount = self.get_open_positions()
        self.entry_amount = amount[-1].get('positionAmt')
        return
    

    def close_position(self):
        positions = self.client.futures_position_information()
        symbol = self.symbol
        for position in positions:
            if position['symbol'] == symbol:
                quantity = abs(float(position['positionAmt']))
                side = "SELL" if float(position['positionAmt']) > 0 else "BUY"

                the_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    type='MARKET',
                    reduceOnly=True
                )

                print(f"Closed position for symbol: {symbol}")
                return the_order

        print(f"No open position found for symbol: {symbol}")

    def get_trade_fees(self):
        fee = self.client.futures_get_trade

