from fastapi import APIRouter, HTTPException
from app.models.crypto import PredictionRequest, PredictionResponse, TechnicalAnalysis
from app.services.technical_analysis import TechnicalAnalyzer
from app.services.ai_predictor import AIPredictor
from app.services.data_fetcher import DataFetcher
from typing import List, Dict
import pandas as pd
from datetime import datetime, timedelta

router = APIRouter()
technical_analyzer = TechnicalAnalyzer()
ai_predictor = AIPredictor()
data_fetcher = DataFetcher()

@router.post("/analyze", response_model=TechnicalAnalysis)
async def analyze_technical_indicators(
    symbol: str,
    interval: str = '1h',
    limit: int = 100
):
    """
    分析指定加密货币的技术指标
    """
    try:
        # 获取历史数据
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=limit)
        df = await data_fetcher.get_historical_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time
        )
        
        # 计算技术指标
        indicators = technical_analyzer.calculate_indicators(df)
        
        return TechnicalAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            **indicators
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict", response_model=PredictionResponse)
async def predict_market_trend(request: PredictionRequest):
    """
    预测市场趋势
    """
    try:
        # 获取技术分析数据
        analysis = await analyze_technical_indicators(
            symbol=request.symbol,
            interval=request.timeframe
        )
        
        # 准备预测数据
        prediction_data = {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "indicators": analysis.dict()
        }
        
        # 进行AI预测
        prediction_result = await ai_predictor.predict(
            prediction_data,
            request.indicators
        )
        
        return PredictionResponse(
            symbol=request.symbol,
            timestamp=datetime.now(),
            **prediction_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols", response_model=List[str])
async def get_available_symbols():
    """
    获取可用的交易对列表
    """
    try:
        tickers = await data_fetcher.get_all_tickers()
        return [ticker['symbol'] for ticker in tickers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ticker/{symbol}", response_model=Dict)
async def get_ticker_info(symbol: str):
    """
    获取指定交易对的详细信息
    """
    try:
        info = await data_fetcher.get_symbol_info(symbol)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades/{symbol}", response_model=List[Dict])
async def get_recent_trades(symbol: str, limit: int = 100):
    """
    获取最近的交易记录
    """
    try:
        trades = await data_fetcher.get_recent_trades(symbol, limit)
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 