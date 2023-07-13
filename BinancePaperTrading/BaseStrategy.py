from connect import DeribitWS
import pandas as pd
import numpy as np
from datetime import datetime as dt
import json


class BaseStrategy:
    def __init__(self, client_id, client_secret, instrument_name, max_holding, ub_mult
                 ,lb_mult, timeframe, trade_capital) -> None:
        

        self.client_id = client_id
        self.cllient_secret = client_secret

        self.derbit = DeribitWS(self.client_id,self.cllient_secret, live=False)
        self.instrument = instrument_name
        self.timeframe = timeframe
        self.trade_capital = trade_capital
        
        self.open_pos = False
        self.entry_price = None
        self.direction = None
        self.target_price = None
        self.stop_price = None
        self.open_price = None
        self.close_price = None



        self.max_holding = max_holding
        self.max_holding_limit = max_holding
        self.fees = 0

        self.ub_mult = ub_mult
        self.lb_mult = lb_mult


        self.trades = {
            "open_timestamp":[],
            "close_timestamp":[],
            "open":[],
            "close":[],
            "fees":[],
            "direction":[],
            "gain":[]
        }

    @staticmethod
    def json_to_df(json_resp):
        df = json_resp['result']
        df = pd.DataFrame(df)
        df['ticks_'] = df.ticks / 1000
        df["time"] = [dt.utcfromtimestamp(date) for date in df["ticks_"]]
        return df
    
    @staticmethod
    def utc_times_now():
        now = int(dt.now().timestamp() * 1000)
        return now
    
    def open_long(self):
        response = self.derbit.market_order(self.instrument, self.trade_capital, "long")
        self.open_pos = True
        self.direction = 1
        try:
            self.open_price = response["result"]["order"]["average_price"]
            self.trades["open_timestamp"].append(dt.now())
            self.target_price = response["result"]["order"]["average_price"] * self.ub_mult
            self.stop_price = response["result"]["order"]["average_price"] * self.lb_mult
            self.entry_price = response["result"]["order"]["average_price"]
            self.trades["open"].append(self.open_price)
            self.fees += response["result"]["order"]["commission"]
        except Exception as e:
            print("ERR IN JSON FOR OPEN_LONG METHOD IN BaseStrategy.py: ", e)

    def open_short(self):
        response = self.derbit.market_order(self.instrument, self.trade_capital, "short")
        self.open_pos = True
        self.direction = -1
        try:
            self.open_price = response["result"]["order"]["average_price"]
            self.trades["open_timestamp"].append(dt.now())
            self.target_price = response["result"]["order"]["average_price"] * self.lb_mult
            self.stop_price = response["result"]["order"]["average_price"] * self.ub_mult
            self.entry_price = response["result"]["order"]["average_price"]
            self.trades["open"].append(response["result"]["order"]["average_price"])
            self.fees += response["result"]["order"]["commission"]
        except Exception as e:
            print("ERR IN JSON FOR OPEN_LONG METHOD IN BaseStrategy.py: ", e)

    def reset_vars(self):
        print("resetting...")
        self.open_pos = False
        self.target_price = None
        self.stop_price = None
        self.direction = None
        self.fees = 0
        self.open_price = None
        self.max_holding = self.max_holding_limit
        self.close_price = None


    def close_pos(self):
        print("Closing Position...")
        response = self.derbit.close_position(self.instrument)
        # try:
        self.close_price = response["result"]["order"]["average_price"]
        self.trades["close_timestamp"].append(dt.now())
        self.trades["close"].append(self.close_price)
        self.fees += response["result"]["order"]["commission"]
        self.trades["fees"].append(self.fees)
        self.trades["direction"].append(self.direction)
        gain = round(((self.close_price-self.open_price)/self.open_price)* self.direction * 100, 4)
        self.trades["gain"].append(gain)
        print(f"""
                Closing position of direction {self.direction},\n
                for a pnl of a {gain}% 
                """)
        # except Exception as e:
        #     print("ERR IN JSON FOR CLOSE_POS METHOD IN BaseStrategy.py: ", e)

        self.reset_vars()

    def monitor_position(self, price):
        print('monitoring...')
        if price >= self.target_price and self.direction == 1:
            self.close_pos()
            print("long target hit")
        elif price <= self.stop_price and self.direction == 1:
            self.close_pos()
            print("long stop hit")
        elif price <= self.target_price and self.direction == -1:
            self.close_pos()
            print("short target hit")
        elif price >=self.stop_price and self.direction == -1:
            self.close_pos()
            print("short stop hit")
        elif self.max_holding <= 0:
            self.close_pos()
            print("Vertical barrier time over")
        else:
            self.max_holding -= 1
        

# with open("BinancePaperTrading/Auth.json") as j:
#     creds = json.load(j)


# client_id = creds['paper']['client_id']
# client_secret = creds['paper']['client_secret']

# b = BaseStrategy(client_id, client_secret, 'BTC-PERPETUAL', 12, 1.02, 0.98, '1h', 100)
# b.monitor_position()

