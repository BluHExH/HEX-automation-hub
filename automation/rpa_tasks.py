"""
RPA / Workflow Automation Module

This module provides functionality for local OS automation tasks including
file operations, email sending, and data processing.

Features:
- Local OS tasks: file ops, email, Excel / CSV processing
- Task scheduling & chaining (sequence of actions)
- Conditional triggers (if/else based on file/content)
- Cross-platform: Linux, Termux (with fallback)

Example:
    config = {
        "tasks": [
            {
                "type": "file_copy",
                "source": "/path/to/source",
                "destination": "/path/to/destination"
            }
        ]
    }
    rpa = RPATasks(config)
    results = rpa.run()
"""

import os
import shutil
import csv
import json
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from typing import Dict, List, Any, Optional
import subprocess
from datetime import datetime

class RPATasks:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tasks = config.get('tasks', [])
        self.schedule = config.get('schedule', '')
        
        # Setup logging
        log_config = config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'rpa_tasks.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def file_copy(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a file from source to destination"""
        try:
            shutil.copy2(source, destination)
            self.logger.info(f"File copied from {source} to {destination}")
            return {
                'task': 'file_copy',
                'status': 'success',
                'source': source,
                'destination': destination
            }
        except Exception as e:
            self.logger.error(f"Failed to copy file from {source} to {destination}: {str(e)}")
            return {
                'task': 'file_copy',
                'status': 'error',
                'error': str(e),
                'source': source,
                'destination': destination
            }
    
    def file_move(self, source: str, destination: str) -> Dict[str, Any]:
        """Move a file from source to destination"""
        try:
            shutil.move(source, destination)
            self.logger.info(f"File moved from {source} to {destination}")
            return {
                'task': 'file_move',
                'status': 'success',
                'source': source,
                'destination': destination
            }
        except Exception as e:
            self.logger.error(f"Failed to move file from {source} to {destination}: {str(e)}")
            return {
                'task': 'file_move',
                'status': 'error',
                'error': str(e),
                'source': source,
                'destination': destination
            }
    
    def file_delete(self, path: str) -> Dict[str, Any]:
        """Delete a file"""
        try:
            os.remove(path)
            self.logger.info(f"File deleted: {path}")
            return {
                'task': 'file_delete',
                'status': 'success',
                'path': path
            }
        except Exception as e:
            self.logger.error(f"Failed to delete file {path}: {str(e)}")
            return {
                'task': 'file_delete',
                'status': 'error',
                'error': str(e),
                'path': path
            }
    
    def directory_create(self, path: str) -> Dict[str, Any]:
        """Create a directory"""
        try:
            os.makedirs(path, exist_ok=True)
            self.logger.info(f"Directory created: {path}")
            return {
                'task': 'directory_create',
                'status': 'success',
                'path': path
            }
        except Exception as e:
            self.logger.error(f"Failed to create directory {path}: {str(e)}")
            return {
                'task': 'directory_create',
                'status': 'error',
                'error': str(e),
                'path': path
            }
    
    def excel_read(self, file_path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """Read data from Excel file"""
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # Convert to JSON-serializable format
            data = df.to_dict('records')
            self.logger.info(f"Excel data read from {file_path}")
            return {
                'task': 'excel_read',
                'status': 'success',
                'file_path': file_path,
                'data': data
            }
        except Exception as e:
            self.logger.error(f"Failed to read Excel file {file_path}: {str(e)}")
            return {
                'task': 'excel_read',
                'status': 'error',
                'error': str(e),
                'file_path': file_path
            }
    
    def excel_write(self, data: List[Dict[str, Any]], file_path: str, sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """Write data to Excel file"""
        try:
            df = pd.DataFrame(data)
            df.to_excel(file_path, sheet_name=sheet_name, index=False)
            self.logger.info(f"Excel data written to {file_path}")
            return {
                'task': 'excel_write',
                'status': 'success',
                'file_path': file_path
            }
        except Exception as e:
            self.logger.error(f"Failed to write Excel file {file_path}: {str(e)}")
            return {
                'task': 'excel_write',
                'status': 'error',
                'error': str(e),
                'file_path': file_path
            }
    
    def csv_read(self, file_path: str) -> Dict[str, Any]:
        """Read data from CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data = list(reader)
            
            self.logger.info(f"CSV data read from {file_path}")
            return {
                'task': 'csv_read',
                'status': 'success',
                'file_path': file_path,
                'data': data
            }
        except Exception as e:
            self.logger.error(f"Failed to read CSV file {file_path}: {str(e)}")
            return {
                'task': 'csv_read',
                'status': 'error',
                'error': str(e),
                'file_path': file_path
            }
    
    def csv_write(self, data: List[Dict[str, Any]], file_path: str) -> Dict[str, Any]:
        """Write data to CSV file"""
        try:
            if not data:
                raise ValueError("No data to write")
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            self.logger.info(f"CSV data written to {file_path}")
            return {
                'task': 'csv_write',
                'status': 'success',
                'file_path': file_path
            }
        except Exception as e:
            self.logger.error(f"Failed to write CSV file {file_path}: {str(e)}")
            return {
                'task': 'csv_write',
                'status': 'error',
                'error': str(e),
                'file_path': file_path
            }
    
    def send_email(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Send email"""
        try:
            smtp_server = config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = config.get('smtp_port', 587)
            sender_email = config.get('sender_email', '')
            sender_password = config.get('sender_password', '')
            recipient_email = config.get('recipient_email', '')
            subject = config.get('subject', '')
            body = config.get('body', '')
            attachments = config.get('attachments', [])
            
            # Create message
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            
            # Add body to email
            message.attach(MIMEText(body, "plain"))
            
            # Add attachments
            for file_path in attachments:
                with open(file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}'
                )
                message.attach(part)
            
            # Create SMTP session
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = message.as_string()
            server.sendmail(sender_email, recipient_email, text)
            server.quit()
            
            self.logger.info(f"Email sent to {recipient_email}")
            return {
                'task': 'send_email',
                'status': 'success',
                'recipient': recipient_email
            }
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return {
                'task': 'send_email',
                'status': 'error',
                'error': str(e)
            }
    
    def run_command(self, command: str) -> Dict[str, Any]:
        """Run a shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            self.logger.info(f"Command executed: {command}")
            return {
                'task': 'run_command',
                'status': 'success',
                'command': command,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {command}")
            return {
                'task': 'run_command',
                'status': 'error',
                'error': 'Command timed out',
                'command': command
            }
        except Exception as e:
            self.logger.error(f"Failed to execute command {command}: {str(e)}")
            return {
                'task': 'run_command',
                'status': 'error',
                'error': str(e),
                'command': command
            }
    
    def check_condition(self, condition: Dict[str, Any]) -> bool:
        """Check a condition for conditional execution"""
        condition_type = condition.get('type')
        
        if condition_type == 'file_exists':
            return os.path.exists(condition.get('path', ''))
        
        elif condition_type == 'file_contains':
            try:
                file_path = condition.get('path', '')
                search_text = condition.get('text', '')
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    return search_text in content
            except:
                return False
        
        elif condition_type == 'directory_empty':
            dir_path = condition.get('path', '')
            if os.path.isdir(dir_path):
                return len(os.listdir(dir_path)) == 0
            return False
        
        else:
            self.logger.warning(f"Unknown condition type: {condition_type}")
            return False
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single RPA task"""
        task_type = task.get('type')
        
        # Check condition if present
        condition = task.get('condition')
        if condition and not self.check_condition(condition):
            self.logger.info(f"Condition not met for task {task_type}, skipping")
            return {
                'task': task_type,
                'status': 'skipped',
                'reason': 'Condition not met'
            }
        
        # Execute task based on type
        if task_type == 'file_copy':
            return self.file_copy(task.get('source', ''), task.get('destination', ''))
        
        elif task_type == 'file_move':
            return self.file_move(task.get('source', ''), task.get('destination', ''))
        
        elif task_type == 'file_delete':
            return self.file_delete(task.get('path', ''))
        
        elif task_type == 'directory_create':
            return self.directory_create(task.get('path', ''))
        
        elif task_type == 'excel_read':
            return self.excel_read(task.get('file_path', ''), task.get('sheet_name'))
        
        elif task_type == 'excel_write':
            return self.excel_write(task.get('data', []), task.get('file_path', ''), task.get('sheet_name', 'Sheet1'))
        
        elif task_type == 'csv_read':
            return self.csv_read(task.get('file_path', ''))
        
        elif task_type == 'csv_write':
            return self.csv_write(task.get('data', []), task.get('file_path', ''))
        
        elif task_type == 'send_email':
            return self.send_email(task.get('config', {}))
        
        elif task_type == 'run_command':
            return self.run_command(task.get('command', ''))
        
        else:
            self.logger.error(f"Unknown task type: {task_type}")
            return {
                'task': task_type,
                'status': 'error',
                'error': f"Unknown task type: {task_type}"
            }
    
    def run(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Main execution method"""
        self.logger.info("Starting RPA tasks")
        
        if dry_run:
            self.logger.info("DRY RUN: No actual RPA tasks will be performed")
            return []
        
        results = []
        
        for task in self.tasks:
            result = self.execute_task(task)
            results.append(result)
            
            # Check if task failed and stop if necessary
            if result.get('status') == 'error' and task.get('stop_on_error', False):
                self.logger.error("Stopping execution due to task failure")
                break
        
        return results