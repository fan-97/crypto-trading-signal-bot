from ast import main
import json
from typing import Dict, List, Optional
import aiohttp
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from .technical_analysis import TechnicalAnalyzer
from core.config import get_settings
import asyncio

class AIAnalyzer:
    def __init__(self):
        """初始化AI分析器"""
        settings = get_settings()
        self.api_key = settings.deepseek_api_key
        self.api_base = "https://api.deepseek.com"
        self.technical_context = {}
        self.technical_analyzer = TechnicalAnalyzer()
        
    def _prepare_market_context(self, symbol: str, market_info: dict) -> str:
        """准备市场分析上下文"""
        current_price = market_info.get('close', 0)
        price_change = market_info.get('price_change', 0)
        price_change_percent = market_info.get('price_change_percent', 0)
        volume = market_info.get('volume', 0)
        
        # 技术指标数据
        indicators = market_info.get('indicators', {})
        
        context = f"""
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
交易对: {symbol}
当前价格: {current_price}
24h涨跌: {price_change} ({price_change_percent}%)
24h成交量: {volume}

技术指标:
1. 趋势指标:
- SMA(20/50/200): {indicators.get('sma_20', 'N/A')}/{indicators.get('sma_50', 'N/A')}/{indicators.get('sma_200', 'N/A')}
- EMA(20/50): {indicators.get('ema_20', 'N/A')}/{indicators.get('ema_50', 'N/A')}
- MACD: {indicators.get('macd', 'N/A')} (Signal: {indicators.get('macd_signal', 'N/A')})
- ADX: {indicators.get('adx', 'N/A')} (DI+: {indicators.get('adx_pos', 'N/A')}, DI-: {indicators.get('adx_neg', 'N/A')})

2. 动量指标:
- RSI: {indicators.get('rsi', 'N/A')}
- Stochastic(K/D): {indicators.get('stoch_k', 'N/A')}/{indicators.get('stoch_d', 'N/A')}
- Williams %R: {indicators.get('williams_r', 'N/A')}

3. 波动指标:
- Bollinger Bands: {indicators.get('bb_upper', 'N/A')}/{indicators.get('bb_middle', 'N/A')}/{indicators.get('bb_lower', 'N/A')}
- ATR: {indicators.get('atr', 'N/A')}

4. 成交量指标:
- OBV: {indicators.get('obv', 'N/A')}
- MFI: {indicators.get('mfi', 'N/A')}
"""
        return context

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _call_ai_api(self, prompt: str) -> Dict:
        """调用 AI API 进行分析"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一位专业的加密货币交易分析师，擅长技术分析和市场研判。"}, 
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,  # 降低随机性，使分析更稳定
                    "max_tokens": 4096,  # 增加输出长度限制
                    "top_p": 0.9,  # 控制输出多样性
                    "frequency_penalty": 0.5  # 降低重复内容
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "content": result['choices'][0]['message']['content']
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"API请求失败: {response.status} - {error_text}")

    async def analyze_market(self, symbol: str, market_info: dict) -> Dict:
        """使用AI分析市场状况"""
        if not self.api_key:
            return {"error": "未配置DeepSeek API密钥"}
            
        try:
            # 计算技术指标
            if 'klines' in market_info:
                market_info['indicators'] = self.technical_analyzer.calculate_indicators(market_info['klines'])
            
            # 准备分析上下文
            context = self._prepare_market_context(symbol, market_info)
            
            # 构建提示词
            prompt = f"""
基于以下市场数据进行专业分析：

{context}

请从以下几个维度进行分析并给出具体建议：

1. 技术面分析
   - 主要趋势研判（短期/中期/长期）
   - 关键技术指标解读（重点关注背离和超买超卖）
   - 形态分析（如有价格形态则指出）

2. 市场结构分析
   - 关键支撑位和阻力位（至少3个）
   - 成交量结构分析
   - 市场情绪评估

3. 交易建议
   - 操作方向和建议（做多/做空/观望）
   - 具体入场价位区间
   - 止损价位（必须给出）
   - 目标获利价位（至少2个）
   - 仓位管理建议

4. 风险提示
   - 潜在风险因素
   - 失效条件
   - 注意事项

请确保分析客观专业，建议具有可操作性，并明确指出数据依据。
"""

            # 调用 AI 接口
            result = await self._call_ai_api(prompt)
            
            # 提取关键点
            key_points = self._extract_key_points(result['content'])
            
            return {
                "success": True,
                "analysis": result['content'],
                "key_points": key_points,
                "timestamp": datetime.now().isoformat(),
                "technical_signals": self.technical_analyzer.get_trend_signal() if 'klines' in market_info else None
            }
                        
        except Exception as e:
            return {
                "error": f"分析过程出错: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            
    def _extract_key_points(self, analysis: str) -> Dict:
        """从AI分析中提取关键点"""
        import re
        
        def extract_price_levels(text: str, pattern: str) -> List[float]:
            """提取价格水平"""
            matches = re.findall(pattern, text)
            return [float(price) for price in matches if price]

        # 趋势判断
        trend_patterns = {
            "强势上涨": 3,
            "上涨": 2,
            "震荡偏多": 1,
            "震荡": 0,
            "震荡偏空": -1,
            "下跌": -2,
            "强势下跌": -3
        }
        
        trend = "震荡"  # 默认
        trend_score = 0
        for pattern, score in trend_patterns.items():
            if pattern in analysis:
                if abs(score) > abs(trend_score):
                    trend = pattern
                    trend_score = score

        # 置信度判断
        confidence = 50  # 默认中等置信度
        confidence_patterns = {
            "明确": 80,
            "强烈": 85,
            "很强": 85,
            "非常": 90,
            "高概率": 75,
            "可能": 60,
            "或许": 55,
            "不确定": 40
        }
        for pattern, value in confidence_patterns.items():
            if pattern in analysis:
                confidence = max(confidence, value)

        # 提取价格水平
        support_levels = extract_price_levels(analysis, r"支撑位?[在于]?[：:]?\s*(\d+\.?\d*)")
        resistance_levels = extract_price_levels(analysis, r"阻力位?[在于]?[：:]?\s*(\d+\.?\d*)")
        stop_loss_levels = extract_price_levels(analysis, r"止损[位]?[在于]?[：:]?\s*(\d+\.?\d*)")
        take_profit_levels = extract_price_levels(analysis, r"目标[位]?[在于]?[：:]?\s*(\d+\.?\d*)")

        return {
            "trend": trend,
            "trend_score": trend_score,  # 趋势得分：-3到3
            "confidence": confidence,    # 置信度：0-100
            "support_levels": sorted(support_levels) if support_levels else None,
            "resistance_levels": sorted(resistance_levels) if resistance_levels else None,
            "stop_loss": min(stop_loss_levels) if stop_loss_levels else None,
            "take_profit_levels": sorted(take_profit_levels) if take_profit_levels else None,
            "risk_level": self._calculate_risk_level(analysis)  # 风险等级：1-5
        }
        
    def _calculate_risk_level(self, analysis: str) -> int:
        """计算风险等级（1-5，5为最高风险）"""
        risk_words = {
            "高风险": 5,
            "风险较大": 4,
            "谨慎": 3,
            "注意风险": 3,
            "风险较小": 2,
            "低风险": 1
        }
        
        risk_level = 3  # 默认中等风险
        for word, level in risk_words.items():
            if word in analysis:
                risk_level = max(risk_level, level)
                
        return risk_level