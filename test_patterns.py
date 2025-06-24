import asyncio
from services.futures_data_fetcher import FuturesDataFetcher
from services.pattern_recognition import PatternRecognition
from datetime import datetime, timedelta

async def main():
    # 创建服务实例
    fetcher = FuturesDataFetcher()
    pattern_recognizer = PatternRecognition()
    
    # 设置查询参数
    symbol = "BTCUSDT"
    intervals = ["15m", "1h", "4h"]  # 分析多个时间周期
    end_time = datetime.now()
    
    for interval in intervals:
        # 根据时间周期设置不同的回溯时间和数据点数量
        if interval == "15m":
            start_time = end_time - timedelta(hours=12)
            limit = 48  # 12小时的15分钟K线
        elif interval == "1h":
            start_time = end_time - timedelta(days=2)
            limit = 48  # 2天的1小时K线
        else:  # 4h
            start_time = end_time - timedelta(days=8)
            limit = 48  # 8天的4小时K线
        
        try:
            # 获取K线数据
            df = await fetcher.get_klines(
                symbol=symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
            
            # 识别形态
            patterns = pattern_recognizer.analyze_patterns(df)
            
            # 打印结果
            print(f"\n{symbol} {interval}周期形态分析:")
            print("=" * 50)
            
            if patterns['bullish']:
                print("\n看涨形态:")
                print("-" * 20)
                for pattern in patterns['bullish']:
                    print(f"- {pattern}")
            
            if patterns['bearish']:
                print("\n看跌形态:")
                print("-" * 20)
                for pattern in patterns['bearish']:
                    print(f"- {pattern}")
                    
            if not patterns['bullish'] and not patterns['bearish']:
                print("未发现明显的反转形态")
            
            # 打印最新K线的基本信息
            latest = df.iloc[-1]
            print(f"\n最新K线信息:")
            print("-" * 20)
            print(f"时间: {latest.name}")
            print(f"开盘: {latest['open']:.2f}")
            print(f"最高: {latest['high']:.2f}")
            print(f"最低: {latest['low']:.2f}")
            print(f"收盘: {latest['close']:.2f}")
            print(f"涨跌幅: {latest['price_change_percent']:.2f}%")
            
        except Exception as e:
            print(f"错误: {str(e)}")
            
        print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(main())
