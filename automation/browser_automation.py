"""
Browser Automation / UI Tasks Module

This module provides functionality for browser automation using Selenium WebDriver.
It supports headless operation, UI interactions, and error handling with screenshots.

Features:
- Headless Chrome / Chromium (Selenium)
- UI interactions (click, fill, extract)
- Screenshot on error
- Remote WebDriver support for Termux fallback
- Logging & retry mechanism

Example:
    config = {
        "headless": true,
        "tasks": [
            {
                "type": "click",
                "selector": "#submit"
            }
        ]
    }
    browser = BrowserAutomation(config)
    results = browser.run()
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging
import time
import os
from typing import Dict, List, Any, Optional

class BrowserAutomation:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.headless = config.get('headless', True)
        self.remote_url = config.get('remote_url', '')
        self.tasks = config.get('tasks', [])
        self.screenshot_dir = config.get('screenshot_dir', 'screenshots')
        self.timeout = config.get('timeout', 30)
        
        # Setup logging
        log_config = config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'browser_automation.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create screenshot directory if it doesn't exist
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        
        self.driver = None
    
    def init_driver(self):
        """Initialize WebDriver"""
        try:
            if self.remote_url:
                # Use remote WebDriver
                self.driver = webdriver.Remote(
                    command_executor=self.remote_url,
                    options=self.get_chrome_options()
                )
            else:
                # Use local WebDriver
                self.driver = webdriver.Chrome(options=self.get_chrome_options())
            
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.implicitly_wait(10)
            
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise e
    
    def get_chrome_options(self):
        """Get Chrome options for WebDriver"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        return options
    
    def take_screenshot(self, name: str):
        """Take a screenshot and save it"""
        if self.driver:
            timestamp = int(time.time())
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single browser task"""
        task_type = task.get('type')
        url = task.get('url', '')
        selector = task.get('selector', '')
        value = task.get('value', '')
        wait_time = task.get('wait', 0)
        
        try:
            # Navigate to URL if provided
            if url:
                self.driver.get(url)
                if wait_time > 0:
                    time.sleep(wait_time)
            
            # Execute task based on type
            if task_type == 'click':
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                element.click()
                
            elif task_type == 'fill':
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                element.clear()
                element.send_keys(value)
                
            elif task_type == 'extract':
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                return {
                    'type': 'extract',
                    'selector': selector,
                    'value': element.text
                }
                
            elif task_type == 'wait':
                time.sleep(value if value else wait_time)
                
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
            
            return {
                'type': task_type,
                'status': 'success'
            }
            
        except TimeoutException as e:
            self.logger.error(f"Timeout while executing task: {task}")
            self.take_screenshot(f"error_{task_type}")
            return {
                'type': task_type,
                'status': 'error',
                'error': f"Timeout: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Error executing task {task}: {str(e)}")
            self.take_screenshot(f"error_{task_type}")
            return {
                'type': task_type,
                'status': 'error',
                'error': str(e)
            }
    
    def run(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Main execution method"""
        self.logger.info("Starting browser automation")
        
        if dry_run:
            self.logger.info("DRY RUN: No actual browser automation will be performed")
            return []
        
        results = []
        
        try:
            self.init_driver()
            
            for task in self.tasks:
                result = self.execute_task(task)
                results.append(result)
                
                # Check if task failed and stop if necessary
                if result.get('status') == 'error' and task.get('stop_on_error', False):
                    self.logger.error("Stopping execution due to task failure")
                    break
            
        except Exception as e:
            self.logger.error(f"Browser automation failed: {str(e)}")
            self.take_screenshot("fatal_error")
        finally:
            if self.driver:
                self.driver.quit()
        
        return results