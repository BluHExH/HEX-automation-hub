"""
Unit tests for social bots module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automation.social_bots import SocialBots

class TestSocialBots(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            "social_bots": {
                "telegram": {
                    "token": "test_token",
                    "chat_id": "test_chat_id"
                },
                "twitter": {
                    "consumer_key": "test_key",
                    "consumer_secret": "test_secret",
                    "access_token": "test_token",
                    "access_token_secret": "test_token_secret"
                }
            },
            "logging": {
                "level": "DEBUG",
                "file": "test_social_bots.log"
            }
        }
    
    def test_init(self):
        """Test SocialBots initialization"""
        with patch('automation.social_bots.Bot') as mock_bot:
            mock_bot_instance = MagicMock()
            mock_bot.return_value = mock_bot_instance
            
            social_bots = SocialBots(self.config)
            
            # Verify configuration was loaded
            self.assertIsNotNone(social_bots.social_configs)
            self.assertIn("telegram", social_bots.social_configs)
            self.assertIn("twitter", social_bots.social_configs)
    
    def test_load_message_templates(self):
        """Test message template loading"""
        with patch('automation.social_bots.Bot'):
            social_bots = SocialBots(self.config)
            
            # Create a temporary template file
            template_content = "Hello {name}!\nWelcome to our service.\nHave a great day!"
            
            with open("test_templates.txt", "w") as f:
                f.write(template_content)
            
            # Load templates
            templates = social_bots.load_message_templates("test_templates.txt")
            
            # Verify templates were loaded
            self.assertEqual(len(templates), 3)
            self.assertEqual(templates[0], "Hello {name}!")
            
            # Clean up
            os.remove("test_templates.txt")
    
    def test_select_random_message(self):
        """Test random message selection"""
        with patch('automation.social_bots.Bot'):
            social_bots = SocialBots(self.config)
            
            templates = [
                "Hello {name}!",
                "Hi {name}, welcome!",
                "Greetings {name}!"
            ]
            
            data = {"name": "John"}
            
            # Select random message
            message = social_bots.select_random_message(templates, data)
            
            # Verify placeholder was replaced
            self.assertIn("John", message)
            self.assertNotIn("{name}", message)

if __name__ == '__main__':
    unittest.main()