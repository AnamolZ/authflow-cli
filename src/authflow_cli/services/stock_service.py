import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
import os
import pandas as pd
import concurrent.futures
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockPrice:
    def __init__(self, stock_symbol: str):
        self.stock_symbol = stock_symbol
        self.url = f'https://finance.yahoo.com/quote/{stock_symbol}/'
        self.price = None

    def scrape_price(self):
        """Scrapes the real-time stock price from Yahoo Finance with a fallback to yfinance."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            price_tag = soup.find('fin-streamer', {
                'data-field': 'regularMarketPrice',
                'data-symbol': self.stock_symbol
            })
            
            if price_tag:
                raw_text = price_tag.text
                clean_text = re.sub(r'[^\d.]', '', raw_text)
                self.price = float(clean_text) if clean_text else None
            
            if not self.price or self.price > 5000:
                ticker = yf.Ticker(self.stock_symbol)
                info = ticker.fast_info
                self.price = round(info['last_price'], 2)
                
        except Exception as e:
            logger.error(f"Error scraping price for {self.stock_symbol}: {e}")
            self.price = None

    def history_training_data(self):
        """Downloads and saves historical stock data for training purposes."""
        try:
            today = datetime.now()
            three_months_ago = today - timedelta(days=90)
            training_data = yf.download(self.stock_symbol, start=three_months_ago, end=today, interval='1d')
            path = f"data/{self.stock_symbol}_training.csv"
            training_data.to_csv(path)
            logger.info(f"History data saved to {path}")
        except Exception as e:
            logger.error(f"Error fetching history for {self.stock_symbol}: {e}")

    def get_stock_info(self):
        """Returns a dictionary containing the stock symbol and its current price."""
        self.scrape_price()
        return {'symbol': self.stock_symbol, 'price': self.price}

class StockInfoFetcher:
    def __init__(self, symbols: list):
        self.symbols = symbols

    def fetch_stock_info(self):
        """Fetches info for all symbols concurrently and returns a combined list."""
        stock_info_list = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(StockPrice(symbol).get_stock_info): symbol for symbol in self.symbols}
            for future in concurrent.futures.as_completed(futures):
                try:
                    stock_info_list.append(future.result())
                except Exception as e:
                    logger.error(f"Execution error: {e}")
        return stock_info_list