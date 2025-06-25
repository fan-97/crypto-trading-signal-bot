import asyncio
from services.futures_data_fetcher import FuturesDataFetcher
from services.technical_analysis import TechnicalAnalyzer
from services.pattern_recognition import PatternRecognition
from services.ai_analyzer import AIAnalyzer
from services.signal_generator import SignalGenerator
from services.telegram_notifier import TelegramNotifier
from datetime import datetime
import pandas as pd

async def test_eth_analysis():
    print("开始分析 ETHUSDT...")
    
    # 初始化组件
    data_fetcher = FuturesDataFetcher()
    tech_analyzer = TechnicalAnalyzer()
    pattern_recognizer = PatternRecognition()
    ai_analyzer = AIAnalyzer()
    signal_generator = SignalGenerator()
    telegram_notifier = TelegramNotifier()
    
    try:
        # 获取K线数据
        print("获取K线数据...")
        klines = await data_fetcher.get_klines("ETHUSDT", "15m")
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                         'close_time', 'quote_volume', 'trades', 'taker_buy_volume',
                                         'taker_buy_quote_volume', 'ignored'])
        
        # 转换数据类型
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        print(f"获取到 {len(df)} 条K线数据")
        
        # 计算技术指标
        print("\n计算技术指标...")
        indicators = tech_analyzer.calculate_indicators(df)
        for key, value in indicators.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
        
        # 识别形态
        print("\n识别价格形态...")
        patterns = pattern_recognizer.analyze_patterns(df)
        if patterns['bullish']:
            print("看涨形态:", ", ".join(patterns['bullish']))
        if patterns['bearish']:
            print("看跌形态:", ", ".join(patterns['bearish']))
            
        # 准备市场数据
        latest_data = {
            'price': float(df['close'].iloc[-1]),
            'volume': float(df['volume'].iloc[-1]),
            'price_change': float(df['close'].iloc[-1] - df['close'].iloc[-2]),
            'price_change_percent': float((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100),
            'indicators': indicators,
            'patterns': patterns
        }
        
        # 调用AI分析
        print("\n开始AI分析...")
        ai_result = await ai_analyzer.analyze_market("ETHUSDT", latest_data)
        
        # 打印AI分析结果
        print("\nAI分析结果:")
        if 'analysis' in ai_result:
            print("分析:", ai_result['analysis'])
        
        if 'key_points' in ai_result:
            kp = ai_result['key_points']
            print(f"\n趋势得分: {kp['trend_score']}")
            print(f"置信度: {kp['confidence']}%")
            print(f"风险等级: {kp['risk_level']}/5")
            
            if kp.get('support_levels'):
                print("支撑位:", ", ".join(map(str, kp['support_levels'])))
            if kp.get('resistance_levels'):
                print("阻力位:", ", ".join(map(str, kp['resistance_levels'])))
        
        # 生成交易信号
        print("\n生成交易信号...")
        signals = await signal_generator.generate_signals(df, ai_result)
        
        # 准备通知消息
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        market_info = {
            'symbol': "ETHUSDT",
            'interval': "15m",
            'price': float(df['close'].iloc[-1]),
            'volume': float(df['volume'].iloc[-1]),
            'price_change': float(df['close'].iloc[-1] - df['close'].iloc[-2]),
            'price_change_percent': float((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100),
            'signals': signals
        }
        
        # 构建通知消息
        message = f"""🔔 {now} - {market_info['symbol']} {market_info['interval']} 市场更新

💰 当前价格: {market_info['price']:.2f}
📈 价格变化: {market_info['price_change']:.2f} ({market_info['price_change_percent']:.2f}%)
📊 成交量: {market_info['volume']:.2f}

🎯 交易信号: {signals['recommendation']['action']}
⚖️ 信心指数: {signals['recommendation']['confidence']:.2f}%

📝 分析原因:
{chr(10).join(f'• {reason}' for reason in signals['recommendation']['reasons'])}"""
        
        # 发送Telegram通知
        print("\n发送Telegram通知...")
        await telegram_notifier.send_message(message)
        print("通知发送完成")
                
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        # 如果出错，也通过Telegram通知
        try:
            await telegram_notifier.send_message(f"❌ ETHUSDT分析过程中出错: {str(e)}")
        except:
            print("发送错误通知失败")

if __name__ == "__main__":
    asyncio.run(test_eth_analysis())
