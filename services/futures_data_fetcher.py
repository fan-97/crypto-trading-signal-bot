from typing import Dict, List, Optional, Union
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import get_settings

settings = get_settings()

class FuturesDataFetcher:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.settings = get_settings()
        
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        获取合约K线数据
        
        参数:
            symbol: 交易对名称 (例如: 'BTCUSDT')
            interval: K线间隔 ('1m','3m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d','3d','1w','1M')
            start_time: 开始时间 (可选)
            end_time: 结束时间 (可选)
            limit: 返回的数据条数，默认500，最大1500
            
        返回:
            pandas.DataFrame 包含以下列:
                - open_time: 开盘时间
                - open: 开盘价
                - high: 最高价
                - low: 最低价
                - close: 收盘价
                - volume: 成交量
                - close_time: 收盘时间
                - quote_volume: 成交额
                - trades: 成交笔数
                - taker_buy_volume: Taker买入成交量
                - taker_buy_quote_volume: Taker买入成交额
        """
        try:
            # 构建请求参数
            # 如果未指定limit，使用配置中的数量
            klines_limit = limit if limit is not None else self.settings.klines_limit
            
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": min(klines_limit, 1500)  # 确保不超过最大限制
            }
            
            # 添加可选参数
            if start_time:
                params["startTime"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["endTime"] = int(end_time.timestamp() * 1000)
                
            # 发送请求
            response = requests.get(
                f"{self.base_url}/fapi/v1/klines",
                params=params
            )
            
            # 检查响应状态
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
                
            # 解析数据
            data = response.json()
            
            # 转换为DataFrame
            df = pd.DataFrame(data, columns=[
                'open_time',      # 开盘时间
                'open',           # 开盘价
                'high',           # 最高价
                'low',            # 最低价
                'close',          # 收盘价
                'volume',         # 成交量
                'close_time',     # 收盘时间
                'quote_volume',   # 成交额
                'trades',         # 成交笔数
                'taker_buy_volume',  # 主动买入成交量
                'taker_buy_quote_volume',  # 主动买入成交额
                'ignore'          # 忽略
            ])
            
            # 数据类型转换
            # 转换所有价格和数量为float
            price_columns = ['open', 'high', 'low', 'close']
            volume_columns = ['volume', 'quote_volume', 'taker_buy_volume', 'taker_buy_quote_volume']
            
            for col in price_columns + volume_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 转换trades为整数
            df['trades'] = df['trades'].astype(int)
                
            # 时间戳转换
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # 设置索引
            df.set_index('open_time', inplace=True)
            
            # 删除无用列
            df.drop('ignore', axis=1, inplace=True)
            
            # 添加计算列
            df['price_change'] = df['close'] - df['open']  # 价格变化
            df['price_change_percent'] = (df['price_change'] / df['open']) * 100  # 价格变化百分比
            df['amplitude'] = ((df['high'] - df['low']) / df['open']) * 100  # 振幅
            df['avg_price'] = df['quote_volume'] / df['volume']  # 平均价格
            df['buy_ratio'] = df['taker_buy_volume'] / df['volume']  # 主动买入比例
            
            return df
            
        except Exception as e:
            raise Exception(f"获取K线数据失败: {str(e)}")
            
    def get_available_intervals(self) -> List[str]:
        """
        返回所有可用的时间间隔
        """
        return [
            '1m', '3m', '5m', '15m', '30m',  # 分钟
            '1h', '2h', '4h', '6h', '8h', '12h',  # 小时
            '1d', '3d',  # 天
            '1w',  # 周
            '1M'   # 月
        ]
