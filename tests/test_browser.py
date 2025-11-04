"""
Unit tests for browser automation module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automation.browser_automation import BrowserAutomation

class TestBrowserAutomation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            "headless": True,
            "remote_url": "",
            "tasks": [
                {
                    "type": "click",
                    "selector": "#submit"
                }
            ],
            "screenshot_dir": "test_screenshots",
            "timeout": 10,
            "logging": {
                "level": "DEBUG",
                "file": "test_browser_automation.log"
            }
        }
    
    def test_init(self):
        """Test BrowserAutomation initialization"""
        browser = BrowserAutomation(self.config)
        self.assertEqual(browser.headless, True)
        self.assertEqual(browser.remote_url, "")
        self.assertEqual(len(browser.tasks), 1)
        self.assertEqual(browser.timeout, 10)
    
    def test_get_chrome_options(self):
        """Test Chrome options generation"""
        browser = BrowserAutomation(self.config)
        options = browser.get_chrome_options()
        
        # Verify headless option is set
        self.assertIn('--headless', options.arguments)
        self.assertIn('--no-sandbox', options.arguments)
    
    @patch('automation.browser_automation.webdriver.Chrome')
    def test_init_driver(self, mock_chrome):
        """Test WebDriver initialization"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        browser = BrowserAutomation(self.config)
        browser.init_driver()
        
        # Verify driver was initialized
        self.assertIsNotNone(browser.driver)
        mock_chrome.assert_called_once()
    
    def test_take_screenshot(self):
        """Test screenshot functionality"""
        with patch('automation.browser_automation.webdriver.Chrome') as mock_chrome:
            mock_driver = MagicMock()
            mock_chrome.return_value = mock_driver
            
            browser = BrowserAutomation(self.config)
            browser.init_driver()
            browser.take_screenshot("test")
            
            # Verify screenshot directory exists
            self.assertTrue(os.path.exists("test_screenshots"))
            
            # Clean up
            if os.path.exists("test_screenshots"):
                import shutil
                shutil.rmtree("test_screenshots")

if __name__ == '__main__':
    unittest.main()