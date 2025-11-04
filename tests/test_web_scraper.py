"""
Unit tests for web scraper module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automation.web_scraper import WebScraper

class TestWebScraper(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            "mode": "static",
            "base_url": "https://httpbin.org",
            "selectors": {
                "title": "h1",
                "content": "p"
            },
            "pagination": {
                "param": "page",
                "start": 1,
                "end": 2
            },
            "retry": 3,
            "delay_range": [0.1, 0.2],
            "logging": {
                "level": "DEBUG",
                "file": "test_web_scraper.log"
            }
        }
    
    def test_init(self):
        """Test WebScraper initialization"""
        scraper = WebScraper(self.config)
        self.assertEqual(scraper.mode, "static")
        self.assertEqual(scraper.base_url, "https://httpbin.org")
        self.assertEqual(scraper.retry_count, 3)
    
    @patch('automation.web_scraper.requests.Session')
    def test_scrape_static(self, mock_session):
        """Test static scraping functionality"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.content = b"<html><h1>Test Title</h1><p>Test Content</p></html>"
        mock_response.raise_for_status.return_value = None
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        scraper = WebScraper(self.config)
        result = scraper.scrape_static("https://httpbin.org")
        
        # Verify the result structure
        self.assertIn("title", result)
        self.assertIn("content", result)
    
    def test_handle_pagination(self):
        """Test pagination URL generation"""
        scraper = WebScraper(self.config)
        urls = scraper.handle_pagination()
        
        # Should generate 2 URLs (start=1, end=2)
        self.assertEqual(len(urls), 2)
        self.assertIn("?page=1", urls[0])
        self.assertIn("?page=2", urls[1])
    
    def test_save_to_csv(self):
        """Test CSV saving functionality"""
        scraper = WebScraper(self.config)
        test_data = [
            {"title": "Test 1", "content": "Content 1"},
            {"title": "Test 2", "content": "Content 2"}
        ]
        
        # Test saving to CSV
        test_file = "test_output.csv"
        scraper.save_to_csv(test_data, test_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(test_file))
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
    
    def test_save_to_jsonl(self):
        """Test JSON Lines saving functionality"""
        scraper = WebScraper(self.config)
        test_data = [
            {"title": "Test 1", "content": "Content 1"},
            {"title": "Test 2", "content": "Content 2"}
        ]
        
        # Test saving to JSONL
        test_file = "test_output.jsonl"
        scraper.save_to_jsonl(test_data, test_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(test_file))
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
    
    def test_save_to_sqlite(self):
        """Test SQLite saving functionality"""
        scraper = WebScraper(self.config)
        test_data = [
            {"title": "Test 1", "content": "Content 1"},
            {"title": "Test 2", "content": "Content 2"}
        ]
        
        # Test saving to SQLite
        test_db = "test_output.db"
        scraper.save_to_sqlite(test_data, test_db)
        
        # Verify file was created
        self.assertTrue(os.path.exists(test_db))
        
        # Clean up
        if os.path.exists(test_db):
            os.remove(test_db)

if __name__ == '__main__':
    unittest.main()