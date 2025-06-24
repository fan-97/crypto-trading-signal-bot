import requests
from typing import Dict, List
import json
from app.core.config import get_settings

settings = get_settings()

class AIPredictor:
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.api_url = "https://api.deepseek.com/v1/predict"  # 示例URL，需要替换为实际的DeepSeek API端点

    async def predict(self, data: Dict, indicators: List[str]) -> Dict:
        """
        使用DeepSeek API进行预测
        """
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