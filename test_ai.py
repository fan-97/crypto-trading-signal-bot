import asyncio
from services.ai_analyzer import AIAnalyzer

if __name__ == "__main__":
    ai_analyzer = AIAnalyzer()

    async def main():
        response = await ai_analyzer.analyze_market("BTCUSDT", {})
        print(response)

    asyncio.run(main())
