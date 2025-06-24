import pandas as pd
import numpy as np
from ta.trend import (
    SMAIndicator, EMAIndicator, MACD, ADXIndicator,
    IchimokuIndicator, PSARIndicator
)
from ta.momentum import (
    RSIIndicator, StochasticOscillator, WilliamsRIndicator,
    ROCIndicator, AwesomeOscillatorIndicator
)
from ta.volatility import (
    BollingerBands, AverageTrueRange, DonchianChannel
)
from ta.volume import (
    VolumeWeightedAveragePrice, OnBalanceVolumeIndicator,
    ForceIndexIndicator, MFIIndicator
)
from typing import Dict, List

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = {}

    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        计算技术指标
        """
        # 趋势指标
        self._calculate_trend_indicators(df)
        
        # 动量指标
        self._calculate_momentum_indicators(df)
        
        # 波动率指标
        self._calculate_volatility_indicators(df)
        
        # 成交量指标
        self._calculate_volume_indicators(df)
        
        return self.indicators

    def _calculate_trend_indicators(self, df: pd.DataFrame):
        """
        计算趋势指标
        """
        # SMA
        sma_20 = SMAIndicator(close=df['close'], window=20)
        sma_50 = SMAIndicator(close=df['close'], window=50)
        sma_200 = SMAIndicator(close=df['close'], window=200)
        self.indicators['sma_20'] = sma_20.sma_indicator().iloc[-1]
        self.indicators['sma_50'] = sma_50.sma_indicator().iloc[-1]
        self.indicators['sma_200'] = sma_200.sma_indicator().iloc[-1]

        # EMA
        ema_20 = EMAIndicator(close=df['close'], window=20)
        ema_50 = EMAIndicator(close=df['close'], window=50)
        self.indicators['ema_20'] = ema_20.ema_indicator().iloc[-1]
        self.indicators['ema_50'] = ema_50.ema_indicator().iloc[-1]

        # MACD
        macd = MACD(close=df['close'])
        self.indicators['macd'] = macd.macd().iloc[-1]
        self.indicators['macd_signal'] = macd.macd_signal().iloc[-1]
        self.indicators['macd_hist'] = macd.macd_diff().iloc[-1]

        # ADX
        adx = ADXIndicator(high=df['high'], low=df['low'], close=df['close'])
        self.indicators['adx'] = adx.adx().iloc[-1]
        self.indicators['adx_pos'] = adx.adx_pos().iloc[-1]
        self.indicators['adx_neg'] = adx.adx_neg().iloc[-1]

        # Ichimoku
        ichimoku = IchimokuIndicator(high=df['high'], low=df['low'])
        self.indicators['ichimoku_a'] = ichimoku.ichimoku_a().iloc[-1]
        self.indicators['ichimoku_b'] = ichimoku.ichimoku_b().iloc[-1]
        self.indicators['ichimoku_base'] = ichimoku.ichimoku_base_line().iloc[-1]
        self.indicators['ichimoku_conv'] = ichimoku.ichimoku_conversion_line().iloc[-1]

        # Parabolic SAR
        psar = PSARIndicator(high=df['high'], low=df['low'], close=df['close'])
        self.indicators['psar'] = psar.psar().iloc[-1]
        self.indicators['psar_up'] = psar.psar_up().iloc[-1]
        self.indicators['psar_down'] = psar.psar_down().iloc[-1]

    def _calculate_momentum_indicators(self, df: pd.DataFrame):
        """
        计算动量指标
        """
        # RSI
        rsi = RSIIndicator(close=df['close'], window=14)
        self.indicators['rsi'] = rsi.rsi().iloc[-1]

        # Stochastic Oscillator
        stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
        self.indicators['stoch_k'] = stoch.stoch().iloc[-1]
        self.indicators['stoch_d'] = stoch.stoch_signal().iloc[-1]

        # Williams %R
        williams = WilliamsRIndicator(high=df['high'], low=df['low'], close=df['close'])
        self.indicators['williams_r'] = williams.williams_r().iloc[-1]

        # Rate of Change
        roc = ROCIndicator(close=df['close'])
        self.indicators['roc'] = roc.roc().iloc[-1]

        # Awesome Oscillator
        ao = AwesomeOscillatorIndicator(high=df['high'], low=df['low'])
        self.indicators['ao'] = ao.awesome_oscillator().iloc[-1]

    def _calculate_volatility_indicators(self, df: pd.DataFrame):
        """
        计算波动率指标
        """
        # Bollinger Bands
        bb = BollingerBands(close=df['close'])
        self.indicators['bb_upper'] = bb.bollinger_hband().iloc[-1]
        self.indicators['bb_middle'] = bb.bollinger_mavg().iloc[-1]
        self.indicators['bb_lower'] = bb.bollinger_lband().iloc[-1]
        self.indicators['bb_width'] = bb.bollinger_wband().iloc[-1]

        # Average True Range
        atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'])
        self.indicators['atr'] = atr.average_true_range().iloc[-1]

        # Donchian Channel
        dc = DonchianChannel(high=df['high'], low=df['low'], close=df['close'])
        self.indicators['dc_upper'] = dc.donchian_channel_hband().iloc[-1]
        self.indicators['dc_middle'] = dc.donchian_channel_mband().iloc[-1]
        self.indicators['dc_lower'] = dc.donchian_channel_lband().iloc[-1]

    def _calculate_volume_indicators(self, df: pd.DataFrame):
        """
        计算成交量指标
        """
        # Volume Weighted Average Price
        vwap = VolumeWeightedAveragePrice(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume']
        )
        self.indicators['vwap'] = vwap.volume_weighted_average_price().iloc[-1]

        # On Balance Volume
        obv = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume'])
        self.indicators['obv'] = obv.on_balance_volume().iloc[-1]

        # Force Index
        fi = ForceIndexIndicator(close=df['close'], volume=df['volume'])
        self.indicators['force_index'] = fi.force_index().iloc[-1]

        # Money Flow Index
        mfi = MFIIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume']
        )
        self.indicators['mfi'] = mfi.money_flow_index().iloc[-1]

    def get_trend_signal(self) -> str:
        """
        基于技术指标生成趋势信号
        """
        # 使用多个指标综合判断
        signals = []
        
        # RSI信号
        if self.indicators['rsi'] > 70:
            signals.append("超买")
        elif self.indicators['rsi'] < 30:
            signals.append("超卖")
            
        # MACD信号
        if self.indicators['macd'] > self.indicators['macd_signal']:
            signals.append("MACD看涨")
        elif self.indicators['macd'] < self.indicators['macd_signal']:
            signals.append("MACD看跌")
            
        # 布林带信号
        if self.indicators['close'] > self.indicators['bb_upper']:
            signals.append("突破上轨")
        elif self.indicators['close'] < self.indicators['bb_lower']:
            signals.append("突破下轨")
            
        # ADX信号
        if self.indicators['adx'] > 25:
            if self.indicators['adx_pos'] > self.indicators['adx_neg']:
                signals.append("强势上涨")
            else:
                signals.append("强势下跌")
                
        # 移动平均线信号
        if (self.indicators['sma_20'] > self.indicators['sma_50'] > self.indicators['sma_200']):
            signals.append("均线多头排列")
        elif (self.indicators['sma_20'] < self.indicators['sma_50'] < self.indicators['sma_200']):
            signals.append("均线空头排列")
            
        # 成交量信号
        if self.indicators['obv'] > 0:
            signals.append("成交量支撑上涨")
        elif self.indicators['obv'] < 0:
            signals.append("成交量支撑下跌")
            
        return " | ".join(signals) if signals else "盘整" 