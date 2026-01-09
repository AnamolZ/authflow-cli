import asyncio
import httpx
from ..auth.service import AuthService
from ..services.stock_service import StockInfoFetcher

async def main():
    """
    Main entry point for the Finance CLI tool.
    Handles user token input and fetches stock information.
    """
    max_attempts = 3
    symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA", "GOOG", "NVDA", "NFLX"]

    print("--- OAuth Finance CLI ---")
    
    for attempt in range(1, max_attempts + 1):
        token = input("Enter your access token (or 'exit'): ")
        if token.lower() == 'exit':
            break

        from ..auth.service import settings, jwt, JWTError
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get("sub")
            if not username:
                raise JWTError()
            
            print(f"Access granted! Welcome, {username}.")
            print("Fetching stock prices...")
            
            fetcher = StockInfoFetcher(symbols)
            stock_infos = fetcher.fetch_stock_info()
            
            for info in stock_infos:
                print(f"Symbol: {info['symbol']:<6} | Price: {info['price']}")
            return

        except JWTError:
            print(f"Access denied! Attempt {attempt}/{max_attempts}.")
            if attempt == max_attempts:
                print("Maximum attempts reached.")

if __name__ == "__main__":
    asyncio.run(main())
