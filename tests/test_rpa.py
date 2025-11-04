"""
Unit tests for RPA tasks module
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automation.rpa_tasks import RPATasks

class TestRPATasks(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            "tasks": [
                {
                    "type": "directory_create",
                    "path": "test_directory"
                }
            ],
            "schedule": "",
            "logging": {
                "level": "DEBUG",
                "file": "test_rpa_tasks.log"
            }
        }
        
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_init(self):
        """Test RPATasks initialization"""
        rpa = RPATasks(self.config)
        self.assertEqual(len(rpa.tasks), 1)
        self.assertEqual(rpa.schedule, "")
    
    def test_directory_create(self):
        """Test directory creation functionality"""
        rpa = RPATasks(self.config)
        test_path = os.path.join(self.test_dir, "new_directory")
        
        result = rpa.directory_create(test_path)
        
        # Verify success
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(test_path))
        self.assertTrue(os.path.isdir(test_path))
    
    def test_file_copy(self):
        """Test file copy functionality"""
        rpa = RPATasks(self.config)
        
        # Create source file
        source_file = os.path.join(self.test_dir, "source.txt")
        dest_file = os.path.join(self.test_dir, "dest.txt")
        
        with open(source_file, "w") as f:
            f.write("Test content")
        
        result = rpa.file_copy(source_file, dest_file)
        
        # Verify success
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(dest_file))
        
        # Verify content
        with open(dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Test content")
    
    def test_file_delete(self):
        """Test file deletion functionality"""
        rpa = RPATasks(self.config)
        
        # Create test file
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content")
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_file))
        
        # Delete file
        result = rpa.file_delete(test_file)
        
        # Verify success
        self.assertEqual(result["status"], "success")
        self.assertFalse(os.path.exists(test_file))
    
    def test_csv_read_write(self):
        """Test CSV read/write functionality"""
        rpa = RPATasks(self.config)
        
        # Test data
        test_data = [
            {"name": "John", "age": "30"},
            {"name": "Jane", "age": "25"}
        ]
        
        # Write CSV
        test_file = os.path.join(self.test_dir, "test.csv")
        result = rpa.csv_write(test_data, test_file)
        
        # Verify write success
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(test_file))
        
        # Read CSV
        read_result = rpa.csv_read(test_file)
        
        # Verify read success
        self.assertEqual(read_result["status"], "success")
        self.assertEqual(len(read_result["data"]), 2)
        self.assertEqual(read_result["data"][0]["name"], "John")
    
    def test_check_condition(self):
        """Test condition checking functionality"""
        rpa = RPATasks(self.config)
        
        # Test file_exists condition
        condition = {
            "type": "file_exists",
            "path": __file__  # This file should exist
        }
        
        result = rpa.check_condition(condition)
        self.assertTrue(result)
        
        # Test file_exists with non-existent file
        condition = {
            "type": "file_exists",
            "path": "/non/existent/file"
        }
        
        result = rpa.check_condition(condition)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()