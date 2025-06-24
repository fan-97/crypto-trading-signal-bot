from typing import Dict, List, Optional
import pandas as pd
from .pattern_recognition import PatternRecognition
from .technical_analysis import TechnicalAnalyzer

class SignalGenerator:
    def __init__(self):
        self.pattern_recognizer = PatternRecognition()
        self.technical_analyzer = TechnicalAnalyzer()
        
    def generate_signals(self, df: pd.DataFrame) -> Dict:
        """
        生成交易信号
        
        参数:
            df: 包含OHLCV数据的DataFrame
            
        返回:
            包含交易信号的字典
        """
        signals = {
            'patterns': {},      # K线形态信号
            'technical': {},     # 技术指标信号
            'recommendation': {} # 综合建议
        }
        
        # 获取形态识别信号
        patterns = self.pattern_recognizer.analyze_patterns(df)
        signals['patterns'] = patterns
        
        # 获取技术指标
        indicators = self.technical_analyzer.calculate_indicators(df)
        signals['technical'] = indicators
        
        # 生成综合建议
        signals['recommendation'] = self._generate_recommendation(patterns, indicators)
        
        return signals
        
    def _generate_recommendation(self, patterns: Dict, indicators: Dict) -> Dict:
        """生成综合交易建议"""
        score = 0  # 交易得分: 正数表示看涨，负数表示看跌
        confidence = 0  # 信心指数: 0-100
        reasons = []  # 建议原因
        
        # 基于形态的评分
        if patterns['bullish']:
            score += len(patterns['bullish']) * 2
            reasons.extend([f"发现看涨形态: {p}" for p in patterns['bullish']])
            
        if patterns['bearish']:
            score -= len(patterns['bearish']) * 2
            reasons.extend([f"发现看跌形态: {p}" for p in patterns['bearish']])
            
        # 基于技术指标的评分
        if 'trend' in indicators:
            if indicators['trend'] == '强势上涨':
                score += 3
                reasons.append("技术指标显示强势上涨")
            elif indicators['trend'] == '强势下跌':
                score -= 3
                reasons.append("技术指标显示强势下跌")
                
        # RSI指标评分
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi > 70:
                score -= 1
                reasons.append(f"RSI超买: {rsi:.2f}")
            elif rsi < 30:
                score += 1
                reasons.append(f"RSI超卖: {rsi:.2f}")
                
        # MACD指标评分
        if all(key in indicators for key in ['macd', 'macd_signal']):
            if indicators['macd'] > indicators['macd_signal']:
                score += 1
                reasons.append("MACD金叉")
            else:
                score -= 1
                reasons.append("MACD死叉")
                
        # 计算信心指数
        total_signals = (len(patterns['bullish']) + len(patterns['bearish']) + 
                        (1 if 'trend' in indicators else 0) +
                        (1 if 'rsi' in indicators else 0) +
                        (1 if 'macd' in indicators else 0))
                        
        confidence = min(abs(score) / total_signals * 100, 100) if total_signals > 0 else 0
        
        # 生成行动建议
        action = self._get_action_recommendation(score, confidence)
        
        return {
            'score': score,
            'confidence': confidence,
            'action': action,
            'reasons': reasons
        }
        
    def _get_action_recommendation(self, score: float, confidence: float) -> str:
        """根据得分和信心指数生成行动建议"""
        if confidence < 40:
            return "建议观望，信号不明确"
            
        if score >= 4 and confidence >= 70:
            return "强烈建议买入"
        elif score >= 2:
            return "建议买入"
        elif score <= -4 and confidence >= 70:
            return "强烈建议卖出"
        elif score <= -2:
            return "建议卖出"
        else:
            return "建议持有"
