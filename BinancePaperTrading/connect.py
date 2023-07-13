import asyncio
import websockets
import json


class DeribitWS:
    def __init__(self, client_id, client_secret, live = False) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self.live = live




        if self.live is False:
            self.url = 'wss://test.deribit.com/ws/api/v2'
        elif self.live is True:
            self.url = 'wss://www.deribit.com/ws/api/v2'
        else:
            raise Exception('live must be Bool, True for real, False for paper.')
        
        self.auth_creds = \
                            {
                    "jsonrpc" : "2.0",
                    "id" : 9929,
                    "method" : "public/auth",
                    "params" : {
                        "grant_type" : "client_credentials",
                        "client_id" : self._client_id,
                        "client_secret" : self._client_secret
                    }
                    }
        self.msg = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": None,
        }
        self.test_creds(self.auth_creds)



        instru1 = self.get_available_instruments("btc")
        instru2 = self.get_available_instruments("eth")
        instru3 = self.get_available_instruments("usdc")


        self.available_instruments = instru1 + instru2 + instru3


    async def pub_api(self,msg):
        async with websockets.connect(self.url) as websocket:
            await websocket.send(msg)
            while websocket.open:
                response = await websocket.recv()
                return json.loads(response)
            
    async def priv_api(self,msg):
        async with websockets.connect(self.url) as websocket:
            await websocket.send(json.dumps(self.auth_creds))
            while websocket.open:
                response = await websocket.recv()
                await websocket.send(msg)
                response = await websocket.recv()
                break
            return json.loads(response)

    @staticmethod
    def async_loop(api, message):
        return asyncio.get_event_loop().run_until_complete(api(message))


    def test_creds(self, msg):
        response = self.async_loop(self.pub_api, json.dumps(msg))
        if 'error' in response.keys():
            print(f"Auth failed with error {response['error']}")
            raise Exception("ERR: ",response['error'])
        else:
            print("Auth successful, proceeding...")


    @staticmethod
    def checker(response):
        if "error" in response.keys():
            raise Exception("ERR: ",response['error'])
        if "result" not in response.keys():
            raise Exception("JSON not as expected: ", response)
        else: return 1

    # Public data acquisition
    def get_klines(self, instrument_name, start_timestamp, end_timestamp, resolution):
        if instrument_name not in self.available_instruments: raise Exception("unavailable instrument name, please choose from: ", ' or '.join(self.available_instruments))
        self.msg["method"] = "public/get_tradingview_chart_data"
        self.msg["params"] = {
                "instrument_name" : instrument_name,
                "start_timestamp" : start_timestamp,
                "end_timestamp" : end_timestamp,
                "resolution" : resolution
        }
        response = self.async_loop(self.pub_api, json.dumps(self.msg))
        self.checker(response)
        return response
    
    def get_order_book(self, instrument_name, depth):
        if instrument_name not in self.available_instruments: raise Exception("unavailable instrument name, please choose from: ", ' or '.join(self.available_instruments))
        params = {
            "instrument_name":instrument_name,
            "depth":depth
        }
        self.msg["method"] = "public/get_order_book"
        self.msg["params"] = params

        response = self.async_loop(self.pub_api, json.dumps(self.msg))
        self.checker(response)
        return response
    
    def get_available_instruments(self, currency:str, kind:str = "future"):
        if currency.upper() not in ["BTC", "ETH", "USDC"]: raise Exception("Currency has to be either BTC, ETH, USDC")
        params = {
            "currency":currency,
            "kind":kind,
            "expired":False,
        }

        self.msg["method"] = "public/get_instruments"
        self.msg["params"] = params
        
        response = self.async_loop(self.pub_api, json.dumps(self.msg))
        self.checker(response)
        return [d["instrument_name"] for d in response["result"]]
    


    def get_last_price(self, instrument_name:str):
        if instrument_name not in self.available_instruments: raise Exception("unavailable instrument name, please choose from: ", ' or '.join(self.available_instruments))
        params={
            "instrument_name":instrument_name
        }
        self.msg["method"] = "public/ticker"
        self.msg["params"] = params
        quote = self.async_loop(self.pub_api, json.dumps(self.msg))
        self.checker(quote)
        return quote['result']['last_price']
    
    #private data posting
    def market_order(self, instrument_name:str, amount:float, direction:str):
        if instrument_name not in self.available_instruments: raise Exception("unavailable instrument name, please choose from: ", ' or '.join(self.available_instruments))
        params= {
            "instrument_name":instrument_name,
            "amount": amount,
            "type":"market"
        }
        if direction.lower()=="long":
            side= "buy"
        elif direction.lower()=="short":
            side = "sell"
        else:
            raise Exception("Direction must be 'long' or 'short'.")

        self.msg["method"] = f"private/{side}"
        self.msg["params"] = params
        response = self.async_loop(self.priv_api, json.dumps(self.msg))
        self.checker(response)
        return response
    
    def limit_order(self, instrument_name:str, amount:float, direction:str, reduce_only:bool, price:float, post_only:bool):
        if instrument_name not in self.available_instruments: raise Exception("unavailable instrument name, please choose from: ", ' or '.join(self.available_instruments))
        params= {
            "instrument_name":instrument_name,
            "amount":amount,
            "type":"limit",
            "price":price,
            "reduce_only":reduce_only,
            "post_only":post_only
        }


        if direction=="long":
            side = "buy"
        elif direction=="short":
            side="short"
        else:
            raise Exception("Direction must be 'long' or 'short'.")
        self.msg["method"] = f"private/{side}"
        self.msg["params"] = params
        response = self.async_loop(self.priv_api, json.dumps(self.msg))
        self.checker(response)
        return response
    
    def close_position(self, instrument_name):
        if instrument_name not in self.available_instruments: raise Exception("unavailable instrument name, please choose from: ", ' or '.join(self.available_instruments))
        params = {
            "instrument_name": instrument_name,
            "type": "market"
        }
        self.msg["method"] = "private/close_position"
        self.msg["params"] = params
        response = self.async_loop(self.priv_api, json.dumps(self.msg))
        self.checker(response)
        return response

    #priv data acquisition
    def acc_summary(self, currency:str, extended:bool = True):
        if currency.upper() not in ["BTC", "ETH", "USDC"]: raise Exception('Currency has to be either BTC, ETH, USDC')
        
        params = {
            "currency": currency.upper(),
            "extended":extended,
        }

        self.msg["method"] = "private/get_account_summary"
        self.msg["params"] = params
        response = self.async_loop(self.priv_api, json.dumps(self.msg))
        self.checker(response)
        return response
    
    def get_positions(self, currency:str):
        if currency.upper() not in ["BTC", "ETH", "USDC"]: raise Exception("Currency has to be either BTC, ETH, USDC")

        params = {
            "currency":currency,
            "kind":"future"
        }

        self.msg["method"] = "private/get_positions"
        self.msg["params"] = params
        response = self.async_loop(self.priv_api, json.dumps(self.msg))
        self.checker(response)
        return response





if __name__ == '__main__':
    with open('BinancePaperTrading/Auth.json') as j:
        creds = json.load(j)

    client_id = creds['paper']['client_id']
    client_secret = creds['paper']['client_secret']

    ws = DeribitWS(client_id=client_id, client_secret=client_secret, live=False).get_klines('adsad', 123123213, 3213213213, '1h')
