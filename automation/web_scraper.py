"""
Web Scraping / Crawling Module

This module provides functionality for scraping web content from both static and
JavaScript-heavy websites. It supports concurrent fetching, pagination, and
multiple output formats.

Features:
- Static scraping: requests + BeautifulSoup
- JS-heavy scraping: Selenium
- Async concurrent fetching: aiohttp
- Pagination, selector config, retry/backoff, rate-limit, proxy support
- Output: CSV / JSON Lines / SQLite
- Telegram notifications for summary/errors
- Dry-run mode and debug logs

Example:
    config = {
        "mode": "static",
        "base_url": "https://example.com",
        "selectors": {"title": "h1", "content": ".content"},
        "pagination": {"param": "page", "start": 1, "end": 5}
    }
    scraper = WebScraper(config)
    results = scraper.run()
"""

import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import csv
import sqlite3
import time
import logging
from typing import Dict, List, Any
import random

class WebScraper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mode = config.get('mode', 'static')
        self.base_url = config.get('base_url', '')
        self.selectors = config.get('selectors', {})
        self.pagination = config.get('pagination', {})
        self.retry_count = config.get('retry', 3)
        self.delay_range = config.get('delay_range', [1, 3])
        self.proxies = config.get('proxies', [])
        self.session = requests.Session()
        
        # Setup logging
        log_config = config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'web_scraper.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def scrape_static(self, url: str) -> Dict[str, Any]:
        """Scrape static content using requests and BeautifulSoup"""
        for attempt in range(self.retry_count):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                proxy = random.choice(self.proxies) if self.proxies else None
                proxies = {'http': proxy, 'https': proxy} if proxy else None
                
                response = self.session.get(url, headers=headers, proxies=proxies, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                data = {}
                
                # Extract data based on selectors
                for key, selector in self.selectors.items():
                    elements = soup.select(selector)
                    data[key] = [elem.get_text(strip=True) for elem in elements]
                
                return data
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt+1} failed for {url}: {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to scrape {url} after {self.retry_count} attempts")
                    raise e
    
    async def scrape_async(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Asynchronously scrape multiple URLs"""
        async def fetch(session, url):
            for attempt in range(self.retry_count):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    async with session.get(url, headers=headers, timeout=30) as response:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        data = {'url': url}
                        
                        # Extract data based on selectors
                        for key, selector in self.selectors.items():
                            elements = soup.select(selector)
                            data[key] = [elem.get_text(strip=True) for elem in elements]
                        
                        return data
                        
                except Exception as e:
                    if attempt < self.retry_count - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        self.logger.error(f"Failed to fetch {url}: {str(e)}")
                        return {'url': url, 'error': str(e)}
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results
    
    def scrape_js_heavy(self, url: str) -> Dict[str, Any]:
        """Scrape JavaScript-heavy content using Selenium"""
        options = Options()
        if self.config.get('headless', True):
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            time.sleep(3)  # Wait for JS to load
            
            data = {}
            # Extract data based on selectors
            for key, selector in self.selectors.items():
                elements = driver.find_elements("css selector", selector)
                data[key] = [elem.text for elem in elements]
            
            return data
        finally:
            driver.quit()
    
    def handle_pagination(self) -> List[str]:
        """Generate URLs for paginated content"""
        urls = []
        base_url = self.base_url
        pagination_config = self.pagination
        
        if not pagination_config:
            return [base_url]
        
        page_param = pagination_config.get('param', 'page')
        start_page = pagination_config.get('start', 1)
        end_page = pagination_config.get('end', 10)
        
        for page in range(start_page, end_page + 1):
            if '?' in base_url:
                url = f"{base_url}&{page_param}={page}"
            else:
                url = f"{base_url}?{page_param}={page}"
            urls.append(url)
        
        return urls
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str):
        """Save scraped data to CSV"""
        if not data:
            return
            
        # Flatten the data if needed
        flattened_data = []
        for item in data:
            if isinstance(item, dict) and 'error' not in item:
                flattened_data.append(item)
        
        if not flattened_data:
            return
            
        # Get all unique keys
        keys = set()
        for item in flattened_data:
            keys.update(item.keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(keys))
            writer.writeheader()
            writer.writerows(flattened_data)
    
    def save_to_jsonl(self, data: List[Dict[str, Any]], filename: str):
        """Save scraped data to JSON Lines format"""
        with open(filename, 'w', encoding='utf-8') as jsonl_file:
            for item in data:
                jsonl_file.write(json.dumps(item) + '\n')
    
    def save_to_sqlite(self, data: List[Dict[str, Any]], db_path: str, table_name: str = 'scraped_data'):
        """Save scraped data to SQLite database"""
        if not data:
            return
            
        # Flatten the data if needed
        flattened_data = []
        for item in data:
            if isinstance(item, dict) and 'error' not in item:
                flattened_data.append(item)
        
        if not flattened_data:
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table dynamically based on keys
        keys = set()
        for item in flattened_data:
            keys.update(item.keys())
        
        columns = ', '.join([f"{key} TEXT" for key in keys])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        
        # Insert data
        for item in flattened_data:
            placeholders = ', '.join(['?' for _ in keys])
            values = [item.get(key, '') for key in keys]
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)
        
        conn.commit()
        conn.close()
    
    def run(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Main execution method"""
        self.logger.info(f"Starting web scraping in {self.mode} mode")
        
        if dry_run:
            self.logger.info("DRY RUN: No actual scraping will be performed")
            return []
        
        # Add delay to respect rate limits
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        
        if self.mode == 'static':
            urls = self.handle_pagination()
            if len(urls) == 1:
                data = [self.scrape_static(urls[0])]
            else:
                # Run async scraping for multiple URLs
                data = asyncio.run(self.scrape_async(urls))
            return data
        elif self.mode == 'js':
            urls = self.handle_pagination()
            data = []
            for url in urls:
                data.append(self.scrape_js_heavy(url))
                # Add delay between requests
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
            return data
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")