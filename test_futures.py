import asyncio
from services.futures_data_fetcher import FuturesDataFetcher
from datetime import datetime, timedelta

def format_price(value):
    return f"{value:,.2f}" if abs(value) >= 1 else f"{value:.6f}"

def format_volume(value):
    if value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value/1_000:.2f}K"
    else:
        return f"{value:.2f}"

async def main():
    # 创建FuturesDataFetcher实例
    fetcher = FuturesDataFetcher()
    
    # 设置查询参数
    symbol = "BTCUSDT"  # 比特币永续合约
    interval = "1h"     # 1小时K线
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)  # 获取最近24小时的数据
    
    try:
        # 获取K线数据
        df = await fetcher.get_klines(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=24  # 24小时的数据
        )
        
        # 打印数据基本信息
        print(f"\n{symbol} {interval}线 数据概览:")
        print("=" * 60)
        print(f"数据时间范围: {df.index[0]} 至 {df.index[-1]}")
        print(f"数据条数: {len(df)}")
        
        # 计算24小时统计数据
        total_volume = df['volume'].sum()
        avg_price = df['quote_volume'].sum() / total_volume
        price_change = df['close'].iloc[-1] - df['open'].iloc[0]
        price_change_percent = (price_change / df['open'].iloc[0]) * 100
        
        print("\n24小时统计:")
        print("-" * 60)
        print(f"总成交量: {format_volume(total_volume)} {symbol[:3]}")
        print(f"平均价格: {format_price(avg_price)} {symbol[-4:]}")
        print(f"价格变化: {format_price(price_change)} ({price_change_percent:+.2f}%)")
        print(f"最高价: {format_price(df['high'].max())}")
        print(f"最低价: {format_price(df['low'].min())}")
        
        print("\n最新K线数据:")
        print("-" * 60)
        latest = df.iloc[-1]
        
        # 基础价格信息
        print("价格信息:")
        print(f"开盘价: {format_price(latest['open'])}")
        print(f"最高价: {format_price(latest['high'])}")
        print(f"最低价: {format_price(latest['low'])}")
        print(f"收盘价: {format_price(latest['close'])}")
        
        # 成交信息
        print("\n成交信息:")
        print(f"成交量: {format_volume(latest['volume'])} {symbol[:3]}")
        print(f"成交额: {format_volume(latest['quote_volume'])} {symbol[-4:]}")
        print(f"成交笔数: {latest['trades']:,}")
        
        # 分析指标
        print("\n分析指标:")
        print(f"价格变化: {format_price(latest['price_change'])} ({latest['price_change_percent']:+.2f}%)")
        print(f"振幅: {latest['amplitude']:.2f}%")
        print(f"均价: {format_price(latest['avg_price'])}")
        print(f"主动买入比例: {latest['buy_ratio']*100:.2f}%")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
