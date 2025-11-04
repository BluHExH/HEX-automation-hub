"""
Unit tests for API automation module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automation.api_automation import APIAutomation

class TestAPIAutomation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            "endpoints": [
                {
                    "url": "https://httpbin.org/get",
                    "method": "GET",
                    "headers": {},
                    "params": {}
                }
            ],
            "concurrency": 2,
            "retry": 3,
            "delay_range": [0.1, 0.2],
            "logging": {
                "level": "DEBUG",
                "file": "test_api_automation.log"
            }
        }
    
    def test_init(self):
        """Test APIAutomation initialization"""
        api = APIAutomation(self.config)
        self.assertEqual(len(api.endpoints), 1)
        self.assertEqual(api.concurrency, 2)
        self.assertEqual(api.retry_count, 3)
    
    @patch('automation.api_automation.aiohttp.ClientSession')
    async def test_make_request(self, mock_session):
        """Test making a single API request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = MagicMock(return_value='{"test": "data"}')
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        api = APIAutomation(self.config)
        result = await api.make_request(self.config["endpoints"][0])
        
        # Verify the result structure
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["url"], "https://httpbin.org/get")
    
    def test_save_to_csv(self):
        """Test CSV saving functionality"""
        api = APIAutomation(self.config)
        test_data = [
            {"url": "https://httpbin.org/get", "status": 200, "data": '{"test": "data"}'},
            {"url": "https://httpbin.org/post", "status": 201, "data": '{"test": "post"}'}
        ]
        
        # Test saving to CSV
        test_file = "test_api_output.csv"
        api.save_to_csv(test_data, test_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(test_file))
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
    
    def test_save_to_json(self):
        """Test JSON saving functionality"""
        api = APIAutomation(self.config)
        test_data = [
            {"url": "https://httpbin.org/get", "status": 200, "data": '{"test": "data"}'},
            {"url": "https://httpbin.org/post", "status": 201, "data": '{"test": "post"}'}
        ]
        
        # Test saving to JSON
        test_file = "test_api_output.json"
        api.save_to_json(test_data, test_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(test_file))
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
    
    def test_save_to_sqlite(self):
        """Test SQLite saving functionality"""
        api = APIAutomation(self.config)
        test_data = [
            {"url": "https://httpbin.org/get", "status": 200, "data": '{"test": "data"}'},
            {"url": "https://httpbin.org/post", "status": 201, "data": '{"test": "post"}'}
        ]
        
        # Test saving to SQLite
        test_db = "test_api_output.db"
        api.save_to_sqlite(test_data, test_db)
        
        # Verify file was created
        self.assertTrue(os.path.exists(test_db))
        
        # Clean up
        if os.path.exists(test_db):
            os.remove(test_db)

if __name__ == '__main__':
    unittest.main()