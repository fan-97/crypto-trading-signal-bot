import aiohttp
from typing import Dict, Optional
from datetime import datetime
import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import get_settings

# 加载环境变量
load_dotenv()

settings = get_settings()

# 从环境变量获取最小信心指数阈值，默认值为70
MIN_CONFIDENCE_THRESHOLD = float(os.getenv('MIN_CONFIDENCE_THRESHOLD', 70))

class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_ids = settings.telegram_chat_ids.split(',')
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
        
    async def send_signal_notification(
        self,
        symbol: str,
        market_info: dict,
        min_confidence: float = None
    ):
        """
        发送交易信号到Telegram
        
        参数:
            symbol: 交易对
            market_info: 市场信息
            min_confidence: 最小信心指数阈值，如果为None则使用环境变量中的设置
        """
        signals = market_info['signals']
        recommendation = signals['recommendation']
        
        # 如果没有指定阈值，使用环境变量中的设置
        if min_confidence is None:
            min_confidence = MIN_CONFIDENCE_THRESHOLD
            
        # 检查信心指数是否达到阈值
        if recommendation['confidence'] < min_confidence:
            print(f"[Telegram通知] 信心指数 {recommendation['confidence']:.2f}% 低于阈值 {min_confidence}%，不发送通知")
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
                
        # 添加AI分析结果
        if 'ai' in signals and signals['ai']:
            ai_result = signals['ai']
            message.extend([
                "",
                "🤖 *AI智能分析*"
            ])
            
            # 检查AI分析是否禁用
            if ai_result.get('disabled', False):
                message.append("_AI分析功能已禁用\. 要启用\, 请在\.env文件中设置ENABLE\_AI\_ANALYSIS=true_")
            elif 'error' in ai_result:
                message.append(f"❌ AI分析错误: {ai_result['error']}")
            else:
                # 根据趋势选择emoji
                trend = ai_result.get('trend', '')
                trend_emoji = "📈" if "看涨" in trend else "📉" if "看跌" in trend else "⭐"
                
                message.append(f"{trend_emoji} 预测趋势: `{trend}`")
                message.append(f"预测值: `{ai_result.get('prediction', 0):.2f}`")
                message.append(f"信心指数: `{ai_result.get('confidence', 0):.2f}`")
                message.append(f"💡 AI建议: `{ai_result.get('recommendation', '未知')}`")
                
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
            # 特别AI相关的决策依据
            if "AI分析" in reason:
                message.append(f"🤖 {reason}")
            else:
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
        elif "建议持有" in action:
            return "🔒"
        elif "建议观望" in action:
            return "🔍"
        else:
            return "⏳"
