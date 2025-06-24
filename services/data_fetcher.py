from binance.client import Client
from binance.exceptions import BinanceAPIException
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
from app.core.config import get_settings
from app.services.cache_service import CacheService

settings = get_settings()

class DataFetcher:
    def __init__(self):
        self.client = Client(
            settings.binance_api_key,
            settings.binance_api_secret
        )
        self.cache = CacheService()
        
    async def get_historical_klines(
        self,
        symbol: str,
        interval: str = '1h',
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        获取历史K线数据
        
        参数:
            symbol: 交易对符号 (例如: 'BTCUSDT')
            interval: K线间隔 ('1m', '5m', '1h', '4h', '1d' 等)
            limit: 获取的K线数量
            start_time: 开始时间
            end_time: 结束时间
        """
        try:
            # 生成缓存键
            cache_key = self.cache.generate_key(
                "klines",
                symbol=symbol,
                interval=interval,
                limit=limit,
                start_time=start_time.isoformat() if start_time else None,
                end_time=end_time.isoformat() if end_time else None
            )
            
            # 尝试从缓存获取数据
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return pd.DataFrame(cached_data)
            
            # 转换时间格式
            start_str = int(start_time.timestamp() * 1000) if start_time else None
            end_str = int(end_time.timestamp() * 1000) if end_time else None
            
            # 获取K线数据
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_str,
                endTime=end_str
            )
            
            # 转换为DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # 数据类型转换
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
                
            # 设置时间索引
            df.set_index('timestamp', inplace=True)
            
            # 缓存数据
            await self.cache.set(
                cache_key,
                df.reset_index().to_dict(orient='records'),
                settings.klines_cache_ttl
            )
            
            return df
            
        except BinanceAPIException as e:
            raise Exception(f"Binance API错误: {str(e)}")
        except Exception as e:
            raise Exception(f"获取数据时出错: {str(e)}")
    
    async def get_symbol_info(self, symbol: str) -> Dict:
        """
        获取交易对信息
        """
        try:
            # 生成缓存键
            cache_key = self.cache.generate_key("symbol_info", symbol=symbol)
            
            # 尝试从缓存获取数据
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            info = self.client.get_symbol_info(symbol)
            result = {
                'symbol': info['symbol'],
                'base_asset': info['baseAsset'],
                'quote_asset': info['quoteAsset'],
                'status': info['status'],
                'filters': info['filters']
            }
            
            # 缓存数据
            await self.cache.set(cache_key, result, settings.cache_ttl)
            
            return result
        except BinanceAPIException as e:
            raise Exception(f"获取交易对信息失败: {str(e)}")
    
    async def get_all_tickers(self) -> List[Dict]:
        """
        获取所有交易对的24小时价格统计
        """
        try:
            # 生成缓存键
            cache_key = "all_tickers"
            
            # 尝试从缓存获取数据
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            tickers = self.client.get_ticker()
            result = [
                {
                    'symbol': ticker['symbol'],
                    'price_change': float(ticker['priceChange']),
                    'price_change_percent': float(ticker['priceChangePercent']),
                    'last_price': float(ticker['lastPrice']),
                    'volume': float(ticker['volume'])
                }
                for ticker in tickers
            ]
            
            # 缓存数据
            await self.cache.set(cache_key, result, settings.ticker_cache_ttl)
            
            return result
        except BinanceAPIException as e:
            raise Exception(f"获取价格统计失败: {str(e)}")
    
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """
        获取最近的交易记录
        """
        try:
            # 生成缓存键
            cache_key = self.cache.generate_key("recent_trades", symbol=symbol, limit=limit)
            
            # 尝试从缓存获取数据
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            trades = self.client.get_recent_trades(symbol=symbol, limit=limit)
            result = [
                {
                    'id': trade['id'],
                    'price': float(trade['price']),
                    'quantity': float(trade['qty']),
                    'time': datetime.fromtimestamp(trade['time'] / 1000),
                    'is_buyer_maker': trade['isBuyerMaker']
                }
                for trade in trades
            ]
            
            # 缓存数据
            await self.cache.set(cache_key, result, settings.ticker_cache_ttl)
            
            return result
        except BinanceAPIException as e:
            raise Exception(f"获取交易记录失败: {str(e)}") 