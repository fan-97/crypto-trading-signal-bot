from typing import Dict, List, Optional
import pandas as pd
from .pattern_recognition import PatternRecognition
from .technical_analysis import TechnicalAnalyzer
from .ai_predictor import AIPredictor

class SignalGenerator:
    def __init__(self):
        self.pattern_recognizer = PatternRecognition()
        self.technical_analyzer = TechnicalAnalyzer()
        self.ai_predictor = AIPredictor()
        
    async def generate_signals(self, df: pd.DataFrame) -> Dict:
        """
        生成交易信号（集成AI分析）
        
        参数:
            df: 包含OHLCV数据的DataFrame
        返回:
            包含交易信号的字典
        """
        signals = {
            'patterns': {},      # K线形态信号
            'technical': {},     # 技术指标信号
            'ai': {},            # AI行情信号
            'recommendation': {} # 综合建议
        }
        # 获取形态识别信号
        patterns = self.pattern_recognizer.analyze_patterns(df)
        signals['patterns'] = patterns
        # 获取技术指标
        indicators = self.technical_analyzer.calculate_indicators(df)
        signals['technical'] = indicators
        # AI行情分析（DeepSeek）
        if self.ai_predictor.is_enabled:
            try:
                # 只传递最后一根K线和主要指标
                latest_data = df.iloc[-1].to_dict()
                indicator_keys = list(indicators.keys())
                ai_result = await self.ai_predictor.predict(latest_data, indicator_keys)
                signals['ai'] = ai_result
            except Exception as e:
                signals['ai'] = {'error': str(e), 'disabled': False}
        else:
            # AI分析未启用
            signals['ai'] = {'disabled': True, 'message': '未启用AI分析'}
        # 生成综合建议（含AI分析）
        signals['recommendation'] = self._generate_recommendation(patterns, indicators, signals['ai'])
        return signals
        
    def _generate_recommendation(self, patterns: Dict, indicators: Dict, ai_result: Dict = None) -> Dict:
        """生成综合交易建议，当指标分析的信心指数超过50%时，再结合AI进行二次分析"""
        score = 0  # 正数看涨，负数看跌
        confidence = 0  # 信心指数
        reasons = []  # 决策依据建议原因
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
                reasons.append(f"RSI超买: {rsi:.2f}")
        # MACD指标评分
        if all(key in indicators for key in ['macd', 'macd_signal']):
            if indicators['macd'] > indicators['macd_signal']:
                score += 1
                reasons.append("MACD金叉")
            else:
                score -= 1
                reasons.append("MACD死叉")
        # AI分析推荐（DeepSeek）
        ai_action = None
        ai_confidence = None
        if ai_result and isinstance(ai_result, dict) and 'recommendation' in ai_result:
            # 检查AI分析是否禁用
            if ai_result.get('disabled', False):
                reasons.append("AI分析未启用")
            else:
                ai_action = ai_result['recommendation']
                ai_confidence = ai_result.get('confidence', None)
                reasons.append(f"AI分析推荐: {ai_action} (信心: {ai_confidence})")
                # 可根据AI信心和建议调整score/confidence
                if ai_action == "建议买入":
                    score += 2
                elif ai_action == "建议卖出":
                    score -= 2
                elif ai_action == "建议持有":
                    score += 0
                elif ai_action == "建议观望":
                    score += 0
                # 若AI信心高于0.7，提升整体信心指数
                if ai_confidence and ai_confidence > 0.7:
                    confidence += 10
        # 计算初始信心指数（基于技术指标和形态）
        total_signals = (len(patterns['bullish']) + len(patterns['bearish']) + 
                        (1 if 'trend' in indicators else 0) +
                        (1 if 'rsi' in indicators else 0) +
                        (1 if 'macd' in indicators else 0))
        initial_confidence = min(abs(score) / total_signals * 100, 100) if total_signals > 0 else 0
        
        # 当初始信心指数超过50%时，再结合AI进行二次分析
        confidence = initial_confidence
        if initial_confidence > 50 and ai_action and not ai_result.get('disabled', False):
            # 记录二次分析信息
            reasons.append(f"初始信心指数: {initial_confidence:.2f}% (超过50%触发AI二次分析)")
            
            # 根据AI分析结果调整信心指数
            ai_weight = 0.3  # AI分析权重30%
            tech_weight = 0.7  # 技术分析权重70%
            
            # 将AI的信心度转换为百分比
            ai_confidence_percent = ai_confidence * 100 if ai_confidence else 0
            
            # 加权平均计算新的信心指数
            confidence = (initial_confidence * tech_weight) + (ai_confidence_percent * ai_weight)
            
            # 根据AI建议与技术分析的一致性调整信心指数
            tech_direction = "bullish" if score > 0 else "bearish" if score < 0 else "neutral"
            ai_direction = ""
            if "买入" in ai_action:
                ai_direction = "bullish"
            elif "卖出" in ai_action:
                ai_direction = "bearish"
            else:
                ai_direction = "neutral"
                
            # 如果方向一致，提升信心指数
            if ai_direction == tech_direction and ai_direction != "neutral":
                confidence += 10
                reasons.append(f"AI分析与技术分析方向一致，信心指数+10%")
            # 如果方向相反，降低信心指数
            elif (ai_direction == "bullish" and tech_direction == "bearish") or \
                 (ai_direction == "bearish" and tech_direction == "bullish"):
                confidence -= 15
                reasons.append(f"AI分析与技术分析方向相反，信心指数-15%")
                
            # 确保信心指数在有效范围内
            confidence = max(0, min(confidence, 100))
            
            # 添加最终信心指数说明
            reasons.append(f"经过AI二次分析后的最终信心指数: {confidence:.2f}%")
        else:
            # 如果不触发二次分析，使用初始信心指数
            if ai_result and ai_result.get('disabled', False):
                reasons.append("AI分析未启用，仅使用技术指标分析")
            elif initial_confidence <= 50:
                reasons.append(f"初始信心指数: {initial_confidence:.2f}% (未达到触发AI二次分析的阈值)")
        # 生成行动建议
        action = self._get_action_recommendation(score, confidence)
        return {
            'score': score,
            'confidence': confidence,
            'action': action,
            'reasons': reasons,
            'ai_action': ai_action,
            'ai_confidence': ai_confidence
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
