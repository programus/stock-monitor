import os
import re
import urllib.parse

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import requests

from stock_data import get_stock_raw_data
from analyze import analyze

def calculate_date_complex_duration(base_date: datetime, duration_str):
    """
    使用复杂的 duration_str (例如 "1y2m5d", "-1y2m5d") 和基准日期计算之前或之后的日期。

    Args:
        base_date_str: 基准日期字符串，格式为 "YYYY-MM-DD"。
        duration_str:  复杂的持续时间字符串，例如 "1y2m5d" (1年2个月5天), "-1y2m5d" (前1年2个月5天)。
                       单位可以是 'y' (年), 'm' (月), 'd' (天), 'h' (小时)，顺序任意。

    Returns:
        计算后的日期，datetime 对象。
    """
    duration_regex = re.compile(r"([+-]?\d+)([ymdh])") # 匹配数字和单位，允许正负号
    duration_parts = duration_regex.findall(duration_str)

    delta_kwargs = {}
    for value, unit in duration_parts:
        value = int(value) # 转换为整数，因为正则表达式返回的是字符串
        if unit == 'y':
            delta_kwargs['years'] = delta_kwargs.get('years', 0) + value
        elif unit == 'm':
            delta_kwargs['months'] = delta_kwargs.get('months', 0) + value
        elif unit == 'd':
            delta_kwargs['days'] = delta_kwargs.get('days', 0) + value
        elif unit == 'h':
            delta_kwargs['hours'] = delta_kwargs.get('hours', 0) + value # 添加小时支持

    if not delta_kwargs:
        raise ValueError("无效的持续时间字符串")

    delta = relativedelta(**delta_kwargs)
    calculated_date = base_date + delta
    return calculated_date


def get_latest_price(stock_raw_data: pd.DataFrame) -> float:
    """
    获取最新的股票价格。

    Args:
        stock_raw_data: 股票原始数据，DataFrame 对象。

    Returns:
        最新的股票价格，float 类型。
    """
    latest_price = stock_raw_data.iloc[-1]['收盘']
    return latest_price


def notify(forecast_df: pd.DataFrame, latest_price: float, notify_price: float):
    url_template = os.environ.get('WX_PUSH_URL', 'https://wxpusher.zjiecode.com/api/send/message/SPT_utRDPNmSiUlV66YTaxWXtND159b3/{message}')
    forecast_df['higher'] = forecast_df['forecast_price'] > notify_price
    higher_df = forecast_df[forecast_df['higher']]
    if url_template and (len(higher_df) > 0 or latest_price > notify_price):
        print(f'股票价格超过 {notify_price}，发送通知...')
        forecast_str = '(Nothing)'
        if (len(higher_df) > 0):
            table_content = ''.join([f'<tr><td>{date.strftime("%Y-%m-%d")}</td><td>{row["forecast_price"]:.2f}</td></tr>' for date, row in higher_df.iterrows()])
            forecast_str = f', 预测结果：<table><tr><th>日期</th><th>预测价格</th></tr>{table_content}</table>'
        message = f'股票价格超过 {notify_price}，昨日收盘 {latest_price}{forecast_str}'
        print(f'发送消息: {message}')
        url = url_template.format(message=urllib.parse.quote(message))
        requests.get(url)
    else:
        print('股票价格未超过，无需发送通知。')


def link_forecast_and_date(forecast_result: pd.Series, start_date: datetime) -> pd.DataFrame:
    forecast_dates = [start_date + relativedelta(days=i) for i in range(1, len(forecast_result) + 1)]
    forecast_df = pd.DataFrame(forecast_result.to_list(), index=forecast_dates, columns=['forecast_price'])
    return forecast_df


# ---- 主程序 ----
if __name__ == '__main__':
    stock_symbol = os.environ.get('STOCK_CODE', '600519')
    date_delta = os.environ.get('STOCK_DURATION', '5y')
    forecast_duration = os.environ.get('STOCK_FORECAST_DURATION', '30')
    notify_price = os.environ.get('STOCK_NOTIFY_PRICE', '1800')
    today = datetime.today()
    print(f'==== {today} ====')
    start_date = calculate_date_complex_duration(today, f'-{date_delta}').strftime('%Y%m%d')
    end_date = today.strftime('%Y%m%d')

    stock_raw_data = get_stock_raw_data(stock_symbol, start_date, end_date, adjust='qfq')

    print(f'analyzing stock {stock_symbol} from {start_date} to {end_date}, {stock_raw_data.shape}...')
    forecast_result = analyze(stock_raw_data, duration=int(forecast_duration), visualize=False)
    print(f'forecast result: {forecast_result}')

    last_date = stock_raw_data.iloc[-1]['日期']
    forecast_from_date = last_date + relativedelta(days=1)
    forecast_df = link_forecast_and_date(forecast_result, forecast_from_date)

    notify(forecast_df, get_latest_price(stock_raw_data), float(notify_price))

    print('Done.')
    print()
