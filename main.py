from  src.scrapper import Crawler
import pandas as pd
from datetime import datetime as dt 
pd.set_option('display.max_columns', None)


crawler = Crawler() 
df = crawler.fetch_all_data() 
today = dt.today().strftime("%Y-%m-%d")
df.to_csv(f"data/meugov_extraction_{today}.csv", index=False ,sep=";", encoding='utf-8', quotechar='"')
