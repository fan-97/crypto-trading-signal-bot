import aiohttp
from typing import Dict, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import get_settings

settings = get_settings()

class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_ids = settings.telegram_chat_ids.split(',')
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
        
    async def send_signal_notification(
        self,
        symbol: str,
        market_info: dict,
        min_confidence: float = 70.0
    ):
        """
        发送交易信号到Telegram
        
        参数:
            symbol: 交易对
            market_info: 市场信息
            min_confidence: 最小信心指数阈值
        """
        signals = market_info['signals']
        recommendation = signals['recommendation']
        
        # 检查信心指数是否达到阈值
        if recommendation['confidence'] < min_confidence:
            return
            
        # 创建消息内容
        message = self._create_message(symbol, market_info)
        
        # 发送到所有配置的聊天
        for chat_id in self.chat_ids:
            await self._send_message(chat_id, message)
            
    def _create_message(self, symbol: str, market_info: dict) -> str:
        """创建Telegram消息"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        signals = market_info['signals']
        recommendation = signals['recommendation']
        
        # 使用emoji美化消息
        message = [
            f"🔔 *交易信号提醒 - {symbol} {market_info['interval']}*",
            f"时间: {now}",
            "",
            "📊 *市场信息*",
            f"价格: `{market_info['price']:.2f}`",
            f"涨跌: `{market_info['price_change']:.2f} ({market_info['price_change_percent']:.2f}%)`",
            f"成交量: `{market_info['volume']:.2f}`",
            "",
            "🎯 *形态信号*"
        ]
        
        # 添加形态信号
        if signals['patterns']['bullish'] or signals['patterns']['bearish']:
            if signals['patterns']['bullish']:
                message.append(f"📈 看涨: {', '.join(signals['patterns']['bullish'])}")
            if signals['patterns']['bearish']:
                message.append(f"📉 看跌: {', '.join(signals['patterns']['bearish'])}")
        else:
            message.append("未发现明显形态信号")
            
        # 添加技术指标
        message.extend([
            "",
            "📈 *技术指标*"
        ])
        
        for indicator, value in signals['technical'].items():
            if isinstance(value, float):
                message.append(f"{indicator}: `{value:.2f}`")
            else:
                message.append(f"{indicator}: `{value}`")
                
        # 添加交易建议
        action_emoji = self._get_action_emoji(recommendation['action'])
        message.extend([
            "",
            "💡 *交易建议*",
            f"{action_emoji} 建议: {recommendation['action']}",
            f"信心指数: `{recommendation['confidence']:.2f}%`",
            "",
            "📝 *决策依据:*"
        ])
        
        for reason in recommendation['reasons']:
            message.append(f"• {reason}")
            
        # 使用Markdown格式连接所有行
        return "\n".join(message)
        
    async def _send_message(self, chat_id: str, message: str):
        """发送Telegram消息"""
        try:
            # 创建SSL上下文
            ssl_context = aiohttp.TCPConnector(
                ssl=False  # 禁用SSL验证
            )
            
            async with aiohttp.ClientSession(connector=ssl_context) as session:
                async with session.post(
                    f"{self.api_base}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        print(f"发送Telegram消息失败: {error_data}")
                        
        except Exception as e:
            print(f"发送Telegram消息出错: {str(e)}")
            
    def _get_action_emoji(self, action: str) -> str:
        """根据建议动作返回对应的emoji"""
        if "强烈建议买入" in action:
            return "🚀"
        elif "建议买入" in action:
            return "📈"
        elif "强烈建议卖出" in action:
            return "⚠️"
        elif "建议卖出" in action:
            return "📉"
        else:
            return "⏳"
