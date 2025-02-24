import functools
import pandas as pd
import akshare as ak


@functools.lru_cache()
def get_stock_raw_data(stock_symbol, start_date, end_date, adjust) -> pd.DataFrame:
    return ak.stock_zh_a_hist(symbol=stock_symbol, adjust=adjust, start_date=start_date, end_date=end_date)
