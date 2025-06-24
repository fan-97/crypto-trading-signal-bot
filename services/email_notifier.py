import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

class EmailNotifier:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.sender_email = settings.sender_email
        self.sender_password = settings.email_password
        self.receiver_emails = settings.receiver_emails.split(',')
        
    async def send_signal_notification(
        self,
        symbol: str,
        market_info: dict,
        min_confidence: float = None
    ):
        """
        发送交易信号邮件
        
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
            print(f"[邮件通知] 信心指数 {recommendation['confidence']:.2f}% 低于阈值 {min_confidence}%，不发送通知")
            return
            
        # 创建邮件内容
        subject = f"交易信号提醒 - {symbol} {market_info['interval']}"
        body = self._create_email_body(symbol, market_info)
        
        # 发送邮件
        await self._send_email(subject, body)
        
    def _create_email_body(self, symbol: str, market_info: dict) -> str:
        """创建邮件正文"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        signals = market_info['signals']
        recommendation = signals['recommendation']
        
        # 使用HTML格式创建邮件
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>{symbol} {market_info['interval']} 交易信号 - {now}</h2>
            
            <h3>市场信息</h3>
            <ul>
                <li>当前价格: {market_info['price']:.2f}</li>
                <li>价格变化: {market_info['price_change']:.2f} ({market_info['price_change_percent']:.2f}%)</li>
                <li>成交量: {market_info['volume']:.2f}</li>
            </ul>
            
            <h3>形态信号</h3>
        """
        
        # 添加形态信号
        if signals['patterns']['bullish'] or signals['patterns']['bearish']:
            if signals['patterns']['bullish']:
                body += f"<p>看涨形态: {', '.join(signals['patterns']['bullish'])}</p>"
            if signals['patterns']['bearish']:
                body += f"<p>看跌形态: {', '.join(signals['patterns']['bearish'])}</p>"
        else:
            body += "<p>未发现明显形态信号</p>"
            
        # 添加技术指标
        body += "<h3>技术指标</h3><ul>"
        for indicator, value in signals['technical'].items():
            if isinstance(value, float):
                body += f"<li>{indicator}: {value:.2f}</li>"
            else:
                body += f"<li>{indicator}: {value}</li>"
        body += "</ul>"
        
        # 添加AI分析结果
        if 'ai' in signals and signals['ai']:
            ai_result = signals['ai']
            body += "<h3>AI智能分析</h3>"
            
            # 检查AI分析是否禁用
            if ai_result.get('disabled', False):
                body += f"<p style='color: #888888;'><i>AI分析功能已禁用。要启用，请在.env文件中设置ENABLE_AI_ANALYSIS=true</i></p>"
            elif 'error' in ai_result:
                body += f"<p style='color: #FF0000;'>AI分析错误: {ai_result['error']}</p>"
            else:
                # 确定AI预测趋势的颜色
                ai_trend_color = "#008000" if "看涨" in ai_result.get('trend', '') else "#FF0000" if "看跌" in ai_result.get('trend', '') else "#FFA500"
                
                body += f"<p>预测趋势: <span style='color: {ai_trend_color}; font-weight: bold;'>{ai_result.get('trend', '未知')}</span></p>"
                body += f"<p>预测值: {ai_result.get('prediction', 0):.2f}</p>"
                body += f"<p>信心指数: {ai_result.get('confidence', 0):.2f}</p>"
                body += f"<p>AI建议: <strong>{ai_result.get('recommendation', '未知')}</strong></p>"
        
        # 添加交易建议
        confidence_color = self._get_confidence_color(recommendation['confidence'])
        action_color = self._get_action_color(recommendation['action'])
        
        body += f"""
            <h3>交易建议</h3>
            <p style="color: {action_color}; font-weight: bold;">
                行动建议: {recommendation['action']}
            </p>
            <p style="color: {confidence_color};">
                信心指数: {recommendation['confidence']:.2f}%
            </p>
            
            <h4>决策依据:</h4>
            <ul>
        """
        
        for reason in recommendation['reasons']:
            # 高亮显示AI相关的决策依据
            if "AI分析" in reason:
                body += f"<li style='color: #0066cc; font-weight: bold;'>{reason}</li>"
            else:
                body += f"<li>{reason}</li>"
            
        body += """
            </ul>
            <hr>
            <p style="font-size: 12px; color: #666;">
                此邮件由自动交易系统生成，包含AI智能分析结果。请勿直接回复。
            </p>
        </body>
        </html>
        """
        
        return body
        
    async def _send_email(self, subject: str, body: str):
        """发送邮件"""
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.receiver_emails)
            
            # 添加HTML内容
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            
    def _get_confidence_color(self, confidence: float) -> str:
        """根据信心指数返回颜色"""
        if confidence >= 80:
            return "#008000"  # 绿色
        elif confidence >= 60:
            return "#FFA500"  # 橙色
        else:
            return "#FF0000"  # 红色
            
    def _get_action_color(self, action: str) -> str:
        """根据建议动作返回颜色"""
        if "买入" in action:
            return "#008000"  # 绿色
        elif "卖出" in action:
            return "#FF0000"  # 红色
        else:
            return "#FFA500"  # 橙色
