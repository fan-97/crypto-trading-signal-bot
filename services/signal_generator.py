from typing import Dict, List, Optional
import pandas as pd
from .pattern_recognition import PatternRecognition
from .technical_analysis import TechnicalAnalyzer
from .ai_analyzer import AIAnalyzer
from core.config import get_settings

class SignalGenerator:
    def __init__(self):
        self.pattern_recognizer = PatternRecognition()
        self.technical_analyzer = TechnicalAnalyzer()
        self.ai_analyzer = AIAnalyzer()
        
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
        # 先生成基础技术分析建议
        base_recommendation = self._generate_base_recommendation(patterns, indicators)
        signals['base_recommendation'] = base_recommendation
        # 打印K线数量
        print("K线数量:", len(df))
        print("基础分析信心指数:", base_recommendation['confidence'])
        # 只有当基础分析的信心指数超过阈值时才调用AI分析
        # 从配置文件中读取阈值
        settings = get_settings()
        confidence_threshold = settings.ai_confidence_threshold
        if base_recommendation['confidence'] >= confidence_threshold:
            try:
                # 准备市场数据
                latest_data = {
                    'close': df['close'].iloc[-1],
                    'high': df['high'].iloc[-1],
                    'low': df['low'].iloc[-1],
                    'volume': df['volume'].iloc[-1],
                    'price_change': df['close'].iloc[-1] - df['close'].iloc[-2],
                    'price_change_percent': ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100,
                    'indicators': indicators,
                    'klines': df
                }
                
                # 调用AI分析
                print("调用AI分析")
                symbol = df.get('symbol', 'Unknown')
                ai_result = await self.ai_analyzer.analyze_market(symbol, latest_data)
                
                if ai_result.get('error'):
                    signals['ai'] = {
                        'error': ai_result['error'],
                        'disabled': False,
                        'timestamp': ai_result.get('timestamp')
                    }
                else:
                    signals['ai'] = {
                        'analysis': ai_result['analysis'],
                        'key_points': ai_result['key_points'],
                        'technical_signals': ai_result.get('technical_signals'),
                        'timestamp': ai_result['timestamp'],
                        'disabled': False
                    }
            except Exception as e:
                signals['ai'] = {
                    'error': str(e),
                    'disabled': False,
                    'timestamp': None
                }
        else:
            signals['ai'] = {
                'disabled': True,
                'reason': f'基础分析信心指数({base_recommendation["confidence"]:.2f}%)未达到触发AI分析的阈值(50%)',
                'timestamp': None
            }
        # 生成综合建议（含AI分析）
        signals['recommendation'] = self._generate_recommendation(patterns, indicators, signals['ai'])
        return signals
        
    def _generate_base_recommendation(self, patterns: Dict, indicators: Dict) -> Dict:
        """生成基础技术分析建议"""
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

    def _generate_recommendation(self, patterns: Dict, indicators: Dict, ai_result: Dict = None) -> Dict:
        """生成综合交易建议，结合基础分析和AI分析结果"""
        # 获取基础分析结果
        base_rec = self._generate_base_recommendation(patterns, indicators)
        score = base_rec['score']
        confidence = base_rec['confidence']
        reasons = base_rec['reasons'].copy()
        
        # 初始化AI相关变量
        ai_action = None
        ai_confidence = None
        
        # 处理AI分析结果
        if ai_result and isinstance(ai_result, dict) and 'key_points' in ai_result:
            key_points = ai_result['key_points']
            
            # 获取AI行动建议
            if key_points['trend_score'] > 0:
                ai_action = "买入"
            elif key_points['trend_score'] < 0:
                ai_action = "卖出"
            else:
                ai_action = "观望"
            
            # 获取置信度
            ai_confidence = key_points['confidence'] / 100
            
            # 添加AI分析结果到原因列表
            if 'analysis' in ai_result:
                reasons.append(f"AI分析结果: {ai_result['analysis'][:200]}...")
            
            # 添加关键价格水平
            if key_points.get('support_levels'):
                reasons.append(f"支撑位: {', '.join(map(str, key_points['support_levels']))}")
            if key_points.get('resistance_levels'):
                reasons.append(f"阻力位: {', '.join(map(str, key_points['resistance_levels']))}")
            
            # 添加风险评估
            risk_level = key_points.get('risk_level', 3)
            reasons.append(f"风险等级: {risk_level}/5")
            
            # 记录AI建议
            reasons.append(f"AI分析推荐: {ai_action} (置信度: {key_points['confidence']}%)")
            
            # 根据AI分析调整分数
            trend_score = key_points['trend_score']
            if abs(trend_score) >= 2:
                score += trend_score * 2
            else:
                score += trend_score
            
            # 根据AI置信度调整总体置信度
            ai_weight = 0.3
            tech_weight = 0.7
            ai_confidence_percent = key_points['confidence']
            
            # 计算加权平均置信度
            confidence = (confidence * tech_weight) + (ai_confidence_percent * ai_weight)
            
            # 根据分析一致性调整置信度
            tech_direction = "bullish" if base_rec['score'] > 0 else "bearish" if base_rec['score'] < 0 else "neutral"
            ai_direction = "bullish" if trend_score > 0 else "bearish" if trend_score < 0 else "neutral"
            
            if ai_direction == tech_direction and ai_direction != "neutral":
                confidence += 10
                reasons.append("AI分析与技术分析方向一致，信心指数+10%")
            elif ai_direction != "neutral" and tech_direction != "neutral" and ai_direction != tech_direction:
                confidence -= 15
                reasons.append("AI分析与技术分析方向相反，信心指数-15%")
            
            # 确保置信度在有效范围内
            confidence = max(0, min(confidence, 100))
        
        # 生成最终建议
        action = self._get_action_recommendation(score, confidence)
        
        return {
            'score': score,
            'confidence': confidence,
            'action': action,
            'reasons': reasons,
            'ai_action': ai_action,
            'ai_confidence': ai_confidence,
            'base_recommendation': base_rec  # 包含基础分析结果
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
