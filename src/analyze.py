import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import pmdarima as pm

# 1. 数据获取 (使用 akshare)
def get_stock_data_akshare(stock_raw_data):
    """使用 akshare 获取股票数据"""
    stock_price_data = stock_raw_data[["日期", "收盘"]].set_index("日期") # 获取日期和收盘价，并将日期设为索引
    return stock_price_data['收盘']  # 返回收盘价 Series

# 2. 数据预处理 (与之前代码相同)
def preprocess_data(data):
    """数据预处理 (例如，可以添加技术指标特征)"""
    # 这里暂时只使用收盘价
    return data

# 3. 模型训练与预测 (与之前代码相同)
def train_predict_arima(data, order=(5,1,0), forecast_steps=30): # ARIMA 模型阶数 (p, d, q) 和预测步长
    """使用 ARIMA 模型训练和预测"""
    model = ARIMA(data, order=order) # 设定 ARIMA 模型阶数
    model_fit = model.fit() # 拟合模型
    forecast = model_fit.forecast(steps=forecast_steps) # 预测未来 forecast_steps 步
    return forecast


def train_predict_arima_auto(data, forecast_steps=30):
    """使用 auto_arima 自动定阶并训练预测"""
    model = pm.auto_arima(data, seasonal=False, stepwise=True,
                          suppress_warnings=True, error_action="ignore", max_order=10, trace=True) # 自动 ARIMA 定阶
    forecast = model.predict(n_periods=forecast_steps) # 预测未来 forecast_steps 步
    return forecast, model # 返回预测结果和模型对象，后续可以查看模型参数


# 4. 结果可视化 (与之前代码相同)
def visualize_results(historical_data, forecast_data):
    """可视化历史数据和预测结果"""
    plt.figure(figsize=(12, 6))
    plt.plot(historical_data, label='Historical Price')
    forecast_index = pd.date_range(historical_data.index[-1], periods=len(forecast_data), freq='B') # 假设预测周期为工作日
    plt.plot(forecast_index, forecast_data, color='red', label='Forecasted Price')
    plt.title(f'Stock Price Forecast')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()


def analyze(stock_data: pd.DataFrame, duration: int = 30, visualize: bool = True) -> pd.Series:
    # 获取股票数据 (使用 akshare)
    try:
        stock_price_data = get_stock_data_akshare(stock_data)
    except ValueError as e:
        print(f"数据获取失败: {e}")
    else: # 只有数据获取成功才进行后续步骤
        # 数据预处理
        processed_data = preprocess_data(stock_price_data)

        # 模型训练和预测
        forecast_result, model = train_predict_arima_auto(processed_data, forecast_steps=duration)

        # 结果可视化
        if visualize:
            visualize_results(processed_data, forecast_result)

        return forecast_result