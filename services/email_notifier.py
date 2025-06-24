import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import get_settings

settings = get_settings()

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
        min_confidence: float = 70.0  # 只发送信心指数高于此值的信号
    ):
        """
        发送交易信号通知邮件
        
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
            body += f"<li>{reason}</li>"
            
        body += """
            </ul>
            <hr>
            <p style="font-size: 12px; color: #666;">
                此邮件由自动交易系统生成，请勿直接回复。
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
