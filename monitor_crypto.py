import asyncio
from services.market_monitor import MarketMonitor
from services.telegram_notifier import TelegramNotifier
from datetime import datetime
import json

async def signal_callback(symbol: str, market_info: dict):
    # 创建通知器
    telegram_notifier = TelegramNotifier()
    """处理市场信号的回调函数"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    signals = market_info['signals']
    
    print(f"\n{now} - {symbol} {market_info['interval']} 市场更新")
    print("=" * 60)
    
    # 打印价格信息
    print(f"当前价格: {market_info['price']:.2f}")
    print(f"价格变化: {market_info['price_change']:.2f} ({market_info['price_change_percent']:.2f}%)")
    print(f"成交量: {market_info['volume']:.2f}")
    
    # 打印形态信号
    if signals['patterns']['bullish'] or signals['patterns']['bearish']:
        print("\n形态信号:")
        if signals['patterns']['bullish']:
            print("看涨形态:", ", ".join(signals['patterns']['bullish']))
        if signals['patterns']['bearish']:
            print("看跌形态:", ", ".join(signals['patterns']['bearish']))
            
    # 打印技术指标
    print("\n技术指标:")
    for indicator, value in signals['technical'].items():
        if isinstance(value, float):
            print(f"{indicator}: {value:.2f}")
        else:
            print(f"{indicator}: {value}")
            
    # 打印交易建议
    recommendation = signals['recommendation']
    print("\n交易建议:")
    print(f"行动建议: {recommendation['action']}")
    print(f"信心指数: {recommendation['confidence']:.2f}%")
    print("\n决策依据:")
    for reason in recommendation['reasons']:
        print(f"- {reason}")
        
    print("-" * 60)
    
    # 发送通知
    await telegram_notifier.send_signal_notification(symbol, market_info)

async def main():
    # 创建市场监控器
    monitor = MarketMonitor()
    
    # 添加信号回调
    monitor.add_callback(signal_callback)
    
    # 设置要监控的交易对和时间周期
    symbols = ["BTCUSDT", "ETHUSDT"]  # 监控BTC和ETH
    intervals = ["15m", "1h", "4h"]   # 监控多个时间周期
    
    try:
        print("开始市场监控...")
        print("按Ctrl+C停止监控")
        
        # 启动监控
        await monitor.start_monitoring(
            symbols=symbols,
            intervals=intervals,
            update_interval=60  # 每60秒更新一次
        )
    except KeyboardInterrupt:
        print("\n停止监控...")
        monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
