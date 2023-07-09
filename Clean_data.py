import pandas as pd
import datetime as dt
class Cleandata:
    def __init__(self, path, name):
        self.df = pd.read_csv(path)
        self.name = name
    def clean(self):
        self.df.columns = ['index','time', 'open', 'high', 'low', 'close', 'volume', 'close time', 'quote asset volume', 'number of trades', 'taker buy base asset volume', 'taker buy quote asset volume', 'ignore']
        self.df.set_index('index')
        self.df = self.df.drop(columns='index').iloc[:, :6]
        self.df.time = self.df.time / 1000
        self.df.time = [dt.datetime.utcfromtimestamp(date) for date in self.df.time]
        self.df.to_csv(self.name+'.csv')
        print(f'saved as {self.name}.csv')
    def retdf(self):
        self.df = self.df.drop(columns='Unnamed: 0')
        self.df.time = pd.to_datetime(self.df.time)
        return self.df


m = Cleandata('/Users/ghaithalmasri/Desktop/fullstackroad/ETHUSDT.csv','ETHCLEANED')



m.clean()