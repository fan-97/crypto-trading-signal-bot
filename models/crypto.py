from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class CryptoData(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    technical_indicators: Dict[str, float]

class PredictionRequest(BaseModel):
    symbol: str
    timeframe: str
    indicators: List[str]

class PredictionResponse(BaseModel):
    symbol: str
    timestamp: datetime
    prediction: float
    confidence: float
    trend: str
    indicators: Dict[str, float]
    recommendation: str

class TechnicalAnalysis(BaseModel):
    symbol: str
    timestamp: datetime
    
    # 趋势指标
    sma_20: Optional[float]
    sma_50: Optional[float]
    sma_200: Optional[float]
    ema_20: Optional[float]
    ema_50: Optional[float]
    macd: Optional[float]
    macd_signal: Optional[float]
    macd_hist: Optional[float]
    adx: Optional[float]
    adx_pos: Optional[float]
    adx_neg: Optional[float]
    ichimoku_a: Optional[float]
    ichimoku_b: Optional[float]
    ichimoku_base: Optional[float]
    ichimoku_conv: Optional[float]
    psar: Optional[float]
    psar_up: Optional[float]
    psar_down: Optional[float]
    
    # 动量指标
    rsi: Optional[float]
    stoch_k: Optional[float]
    stoch_d: Optional[float]
    williams_r: Optional[float]
    roc: Optional[float]
    ao: Optional[float]
    
    # 波动率指标
    bb_upper: Optional[float]
    bb_middle: Optional[float]
    bb_lower: Optional[float]
    bb_width: Optional[float]
    atr: Optional[float]
    dc_upper: Optional[float]
    dc_middle: Optional[float]
    dc_lower: Optional[float]
    
    # 成交量指标
    vwap: Optional[float]
    obv: Optional[float]
    force_index: Optional[float]
    mfi: Optional[float] 