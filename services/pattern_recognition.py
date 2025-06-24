import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class PatternRecognition:
    def __init__(self):
        # 设置形态识别的参数
        self.doji_size = 0.1  # 十字线实体与影线比例阈值
        self.hammer_ratio = 0.6  # 锤子线下影线与整体长度的比例阈值
        self.engulfing_ratio = 1.2  # 吞没形态的最小比例
        
    def analyze_patterns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        分析K线形态
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            包含看涨和看跌形态的字典
        """
        patterns = {
            'bullish': [],  # 看涨形态
            'bearish': []   # 看跌形态
        }
        
        # 计算K线属性
        self._calculate_candle_properties(df)
        
        # 获取最新的几根K线
        last_candles = df.tail(3)  # 用于识别三根K线形态
        last_two = df.tail(2)      # 用于识别两根K线形态
        latest = df.iloc[-1]       # 最新K线
        
        # 识别单根K线形态
        self._identify_hammer(latest, patterns)
        self._identify_shooting_star(latest, patterns)
        self._identify_hanging_man(latest, df, patterns)
        
        # 识别两根K线形态
        if len(last_two) == 2:
            self._identify_engulfing(last_two, patterns)
            
        # 识别三根K线形态
        if len(last_candles) == 3:
            self._identify_morning_star(last_candles, patterns)
            self._identify_evening_star(last_candles, patterns)
            self._identify_tweezer_bottom(last_candles, patterns)
            
        return patterns
    
    def _calculate_candle_properties(self, df: pd.DataFrame):
        """计算K线的基本属性"""
        # 计算实体
        df['body'] = df['close'] - df['open']
        df['body_size'] = abs(df['body'])
        
        # 计算上下影线
        df['upper_shadow'] = df.apply(
            lambda x: x['high'] - max(x['open'], x['close']), axis=1
        )
        df['lower_shadow'] = df.apply(
            lambda x: min(x['open'], x['close']) - x['low'], axis=1
        )
        
        # 计算K线总长度
        df['total_length'] = df['high'] - df['low']
        
        # 判断是否为阳线或阴线
        df['is_bullish'] = df['close'] > df['open']
        
    def _identify_hammer(self, candle: pd.Series, patterns: Dict):
        """识别锤子线形态"""
        if (candle['lower_shadow'] > candle['total_length'] * self.hammer_ratio and
            candle['upper_shadow'] < candle['body_size'] * 0.3 and
            candle['is_bullish']):
            patterns['bullish'].append('锤子线')
            
    def _identify_shooting_star(self, candle: pd.Series, patterns: Dict):
        """识别流星线形态"""
        if (candle['upper_shadow'] > candle['total_length'] * self.hammer_ratio and
            candle['lower_shadow'] < candle['body_size'] * 0.3 and
            not candle['is_bullish']):
            patterns['bearish'].append('流星线')
            
    def _identify_hanging_man(self, candle: pd.Series, df: pd.DataFrame, patterns: Dict):
        """识别上吊线形态"""
        if (candle['lower_shadow'] > candle['total_length'] * self.hammer_ratio and
            candle['upper_shadow'] < candle['body_size'] * 0.3 and
            not candle['is_bullish'] and
            df['close'].iloc[-2] > candle['close']):
            patterns['bearish'].append('上吊线')
            
    def _identify_engulfing(self, candles: pd.DataFrame, patterns: Dict):
        """识别吞没形态"""
        prev, curr = candles.iloc[0], candles.iloc[1]
        
        # 看涨吞没
        if (not prev['is_bullish'] and curr['is_bullish'] and
            curr['body_size'] > prev['body_size'] * self.engulfing_ratio and
            curr['open'] < prev['close'] and curr['close'] > prev['open']):
            patterns['bullish'].append('看涨吞没')
            
        # 看跌吞没
        elif (prev['is_bullish'] and not curr['is_bullish'] and
              curr['body_size'] > prev['body_size'] * self.engulfing_ratio and
              curr['open'] > prev['close'] and curr['close'] < prev['open']):
            patterns['bearish'].append('看跌吞没')
            
    def _identify_morning_star(self, candles: pd.DataFrame, patterns: Dict):
        """识别早晨之星形态"""
        first, second, third = candles.iloc[0], candles.iloc[1], candles.iloc[2]
        
        if (not first['is_bullish'] and  # 第一根是阴线
            abs(second['body']) < first['body_size'] * 0.3 and  # 第二根是小实体
            third['is_bullish'] and  # 第三根是阳线
            third['close'] > first['open'] + first['body'] / 2):  # 第三根收盘价超过第一根实体的一半
            patterns['bullish'].append('早晨之星')
            
    def _identify_evening_star(self, candles: pd.DataFrame, patterns: Dict):
        """识别黄昏之星形态"""
        first, second, third = candles.iloc[0], candles.iloc[1], candles.iloc[2]
        
        if (first['is_bullish'] and  # 第一根是阳线
            abs(second['body']) < first['body_size'] * 0.3 and  # 第二根是小实体
            not third['is_bullish'] and  # 第三根是阴线
            third['close'] < first['close'] - first['body'] / 2):  # 第三根收盘价低于第一根实体的一半
            patterns['bearish'].append('黄昏之星')
            
    def _identify_tweezer_bottom(self, candles: pd.DataFrame, patterns: Dict):
        """识别双针探底形态"""
        first, second, third = candles.iloc[0], candles.iloc[1], candles.iloc[2]
        
        # 检查最后两根K线的低点是否接近
        if (abs(second['low'] - third['low']) < second['total_length'] * 0.1 and
            not second['is_bullish'] and third['is_bullish'] and
            second['low'] < first['low']):  # 确保是在低点
            patterns['bullish'].append('双针探底')
