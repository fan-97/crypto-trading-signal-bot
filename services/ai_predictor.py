import requests
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥和设置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')

# AI分析功能开关，默认启用
ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'

class AIPredictor:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = "https://api.deepseek.com"  # 示例URL，需要替换为实际的DeepSeek API端点
        self.enabled = ENABLE_AI_ANALYSIS  # AI分析功能开关
        
    @property
    def is_enabled(self) -> bool:
        """检查AI分析功能是否启用"""
        return self.enabled and bool(self.api_key)

    async def predict(self, data: Dict, indicators: List[str]) -> Optional[Dict]:
        """
        使用DeepSeek API进行预测
        
        如果AI分析功能未启用，返回None
        """
        # 检查AI分析功能是否启用
        if not self.is_enabled:
            return {
                "prediction": 0.5,
                "confidence": 0,
                "trend": "未启用AI分析",
                "recommendation": "未启用AI分析",
                "disabled": True
            }
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "data": data,
                "indicators": indicators,
                "model": "crypto-prediction"
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return self._process_prediction(result)
            else:
                raise Exception(f"API请求失败: {response.status_code}")

        except Exception as e:
            raise Exception(f"预测过程出错: {str(e)}")

    def _process_prediction(self, result: Dict) -> Dict:
        """
        处理预测结果
        """
        prediction = result.get("prediction", 0)
        confidence = result.get("confidence", 0)

        return {
            "prediction": prediction,
            "confidence": confidence,
            "trend": self._get_trend(prediction),
            "recommendation": self._get_recommendation(prediction, confidence)
        }

    def _get_trend(self, prediction: float) -> str:
        """
        根据预测值确定趋势
        """
        if prediction > 0.6:
            return "强烈看涨"
        elif prediction > 0.5:
            return "看涨"
        elif prediction < 0.4:
            return "强烈看跌"
        elif prediction < 0.5:
            return "看跌"
        else:
            return "中性"

    def _get_recommendation(self, prediction: float, confidence: float) -> str:
        """
        生成交易建议
        """
        if confidence < 0.6:
            return "建议观望"
        
        if prediction > 0.6:
            return "建议买入"
        elif prediction < 0.4:
            return "建议卖出"
        else:
            return "建议持有" 