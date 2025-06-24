import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import pandas as pd
from .futures_data_fetcher import FuturesDataFetcher
from .signal_generator import SignalGenerator

class MarketMonitor:
    def __init__(self):
        self.data_fetcher = FuturesDataFetcher()
        self.signal_generator = SignalGenerator()
        self.monitoring = False
        self.callbacks = []
        
    def add_callback(self, callback: Callable[[str, Dict], None]):
        """添加信号回调函数"""
        self.callbacks.append(callback)
        
    def remove_callback(self, callback: Callable[[str, Dict], None]):
        """移除信号回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            
    async def start_monitoring(
        self,
        symbols: List[str],
        intervals: List[str],
        update_interval: int = 60
    ):
        """
        开始市场监控
        
        参数:
            symbols: 要监控的交易对列表
            intervals: 要监控的时间周期列表
            update_interval: 更新间隔（秒）
        """
        self.monitoring = True
        
        while self.monitoring:
            try:
                for symbol in symbols:
                    for interval in intervals:
                        # 获取K线数据
                        df = await self.data_fetcher.get_klines(
                            symbol=symbol,
                            interval=interval,
                            limit=100  # 获取足够的历史数据用于分析
                        )
                        
                        # 生成信号
                        signals = self.signal_generator.generate_signals(df)
                        
                        # 添加基本市场信息
                        latest = df.iloc[-1]
                        market_info = {
                            'symbol': symbol,
                            'interval': interval,
                            'timestamp': latest.name,
                            'price': latest['close'],
                            'price_change': latest['price_change'],
                            'price_change_percent': latest['price_change_percent'],
                            'volume': latest['volume'],
                            'signals': signals
                        }
                        
                        # 调用回调函数
                        for callback in self.callbacks:
                            await callback(symbol, market_info)
                            
                # 等待下一次更新
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                print(f"监控错误: {str(e)}")
                await asyncio.sleep(5)  # 发生错误时等待5秒后重试
                
    def stop_monitoring(self):
        """停止市场监控"""
        self.monitoring = False
