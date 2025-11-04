"""
API Automation / ETL Module

This module provides functionality for automating API interactions with
support for multiple HTTP methods, concurrent requests, and data processing.

Features:
- Configurable endpoints: GET/POST/PUT/DELETE
- Async API requests (aiohttp)
- Retry + backoff + rate-limit
- Response processing + storage (DB / CSV / JSON)
- Scheduled run: cron / Celery / GitHub Actions
- Webhook / Slack / Telegram notifications

Example:
    config = {
        "endpoints": [
            {
                "url": "https://api.example.com/data",
                "method": "GET"
            }
        ],
        "concurrency": 5
    }
    async with APIAutomation(config) as api:
        results = await api.run()
"""

import asyncio
import aiohttp
import httpx
import json
import csv
import sqlite3
import logging
from typing import Dict, List, Any, Optional
import time
import random
from datetime import datetime

class APIAutomation:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.endpoints = config.get('endpoints', [])
        self.concurrency = config.get('concurrency', 5)
        self.retry_count = config.get('retry', 3)
        self.delay_range = config.get('delay_range', [1, 3])
        self.session = None
        
        # Setup logging
        log_config = config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'api_automation.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Make a single API request with retry logic"""
        url = endpoint.get('url')
        method = endpoint.get('method', 'GET').upper()
        headers = endpoint.get('headers', {})
        params = endpoint.get('params', {})
        data = endpoint.get('data', {})
        
        for attempt in range(self.retry_count):
            try:
                # Add delay to respect rate limits
                delay = random.uniform(*self.delay_range)
                await asyncio.sleep(delay)
                
                if method == 'GET':
                    async with self.session.get(url, headers=headers, params=params, timeout=30) as response:
                        response_data = await response.text()
                        return {
                            'url': url,
                            'status': response.status,
                            'headers': dict(response.headers),
                            'data': response_data
                        }
                elif method == 'POST':
                    async with self.session.post(url, headers=headers, params=params, json=data, timeout=30) as response:
                        response_data = await response.text()
                        return {
                            'url': url,
                            'status': response.status,
                            'headers': dict(response.headers),
                            'data': response_data
                        }
                elif method == 'PUT':
                    async with self.session.put(url, headers=headers, params=params, json=data, timeout=30) as response:
                        response_data = await response.text()
                        return {
                            'url': url,
                            'status': response.status,
                            'headers': dict(response.headers),
                            'data': response_data
                        }
                elif method == 'DELETE':
                    async with self.session.delete(url, headers=headers, params=params, timeout=30) as response:
                        response_data = await response.text()
                        return {
                            'url': url,
                            'status': response.status,
                            'headers': dict(response.headers),
                            'data': response_data
                        }
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
            except Exception as e:
                self.logger.warning(f"Attempt {attempt+1} failed for {url}: {str(e)}")
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {self.retry_count} attempts")
                    return {
                        'url': url,
                        'error': str(e)
                    }
    
    async def run_async(self) -> List[Dict[str, Any]]:
        """Run all API requests concurrently"""
        self.logger.info(f"Starting API automation with {len(self.endpoints)} endpoints")
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.concurrency)
        
        async def bounded_request(endpoint):
            async with semaphore:
                return await self.make_request(endpoint)
        
        # Create tasks for all endpoints
        tasks = [bounded_request(endpoint) for endpoint in self.endpoints]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Request failed with exception: {str(result)}")
                processed_results.append({'error': str(result)})
            else:
                processed_results.append(result)
        
        return processed_results
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str):
        """Save API response data to CSV"""
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
    
    def save_to_json(self, data: List[Dict[str, Any]], filename: str):
        """Save API response data to JSON"""
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)
    
    def save_to_sqlite(self, data: List[Dict[str, Any]], db_path: str, table_name: str = 'api_data'):
        """Save API response data to SQLite database"""
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
        
        # Define column types (simplified)
        columns = ', '.join([f"{key} TEXT" for key in keys])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        
        # Insert data
        for item in flattened_data:
            placeholders = ', '.join(['?' for _ in keys])
            values = [str(item.get(key, '')) for key in keys]
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)
        
        conn.commit()
        conn.close()
    
    async def run(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Main execution method"""
        self.logger.info("Starting API automation")
        
        if dry_run:
            self.logger.info("DRY RUN: No actual API requests will be made")
            return []
        
        async with self:
            results = await self.run_async()
            return results