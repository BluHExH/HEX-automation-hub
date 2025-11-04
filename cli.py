#!/usr/bin/env python3
"""
Command Line Interface for HEX Automation Hub
"""

import argparse
import sys
import asyncio
import json
from typing import Dict, Any
from automation.web_scraper import WebScraper
from automation.api_automation import APIAutomation
from automation.browser_automation import BrowserAutomation
from automation.rpa_tasks import RPATasks
from automation.social_bots import SocialBots
from automation.utils import load_config, setup_logging, setup_signal_handlers

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='HEX Automation Hub - Multi-purpose automation tool')
    
    parser.add_argument(
        'command',
        choices=['run', 'test-target', 'export'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--target',
        choices=['web_scraper', 'api', 'browser', 'rpa', 'social_bots'],
        help='Target automation module'
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'sqlite'],
        help='Export format'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (default behavior)'
    )
    
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run in daemon mode (loop mode)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without executing actions'
    )
    
    return parser.parse_args()

async def run_web_scraper(config: Dict[str, Any], dry_run: bool = False):
    """Run web scraper"""
    scraper_config = config.get('web_scraper', {})
    scraper = WebScraper(scraper_config)
    
    try:
        results = scraper.run(dry_run=dry_run)
        
        # Save results based on storage config
        storage_config = config.get('storage', {})
        storage_type = storage_config.get('type', 'csv')
        storage_path = storage_config.get('path', 'data/web_scraper_output.csv')
        
        if storage_type == 'csv':
            scraper.save_to_csv(results, storage_path)
        elif storage_type == 'json':
            scraper.save_to_jsonl(results, storage_path.replace('.csv', '.jsonl'))
        elif storage_type == 'sqlite':
            scraper.save_to_sqlite(results, storage_path, 'web_scraping')
        
        print(f"Web scraping completed. Results saved to {storage_path}")
        return results
    except Exception as e:
        print(f"Web scraping failed: {str(e)}")
        return []

async def run_api_automation(config: Dict[str, Any], dry_run: bool = False):
    """Run API automation"""
    api_config = config.get('api', {})
    
    async with APIAutomation(api_config) as api:
        try:
            results = await api.run(dry_run=dry_run)
            
            # Save results based on storage config
            storage_config = config.get('storage', {})
            storage_type = storage_config.get('type', 'json')
            storage_path = storage_config.get('path', 'data/api_output.json')
            
            if storage_type == 'csv':
                api.save_to_csv(results, storage_path.replace('.json', '.csv'))
            elif storage_type == 'json':
                api.save_to_json(results, storage_path)
            elif storage_type == 'sqlite':
                api.save_to_sqlite(results, storage_path.replace('.json', '.db'), 'api_data')
            
            print(f"API automation completed. Results saved to {storage_path}")
            return results
        except Exception as e:
            print(f"API automation failed: {str(e)}")
            return []

async def run_browser_automation(config: Dict[str, Any], dry_run: bool = False):
    """Run browser automation"""
    browser_config = config.get('browser', {})
    browser = BrowserAutomation(browser_config)
    
    try:
        results = browser.run(dry_run=dry_run)
        print("Browser automation completed.")
        return results
    except Exception as e:
        print(f"Browser automation failed: {str(e)}")
        return []

async def run_rpa_tasks(config: Dict[str, Any], dry_run: bool = False):
    """Run RPA tasks"""
    rpa_config = config.get('rpa', {})
    rpa = RPATasks(rpa_config)
    
    try:
        results = rpa.run(dry_run=dry_run)
        print("RPA tasks completed.")
        return results
    except Exception as e:
        print(f"RPA tasks failed: {str(e)}")
        return []

async def run_social_bots(config: Dict[str, Any], dry_run: bool = False):
    """Run social bots"""
    social_config = config.get('social_bots', {})
    social_bots = SocialBots(config)  # Pass full config
    
    try:
        results = await social_bots.run(dry_run=dry_run)
        print("Social bots automation completed.")
        return results
    except Exception as e:
        print(f"Social bots automation failed: {str(e)}")
        return []

async def run_target(config: Dict[str, Any], target: str, dry_run: bool = False):
    """Run a specific target"""
    if target == 'web_scraper':
        return await run_web_scraper(config, dry_run)
    elif target == 'api':
        return await run_api_automation(config, dry_run)
    elif target == 'browser':
        return await run_browser_automation(config, dry_run)
    elif target == 'rpa':
        return await run_rpa_tasks(config, dry_run)
    elif target == 'social_bots':
        return await run_social_bots(config, dry_run)
    else:
        raise ValueError(f"Unknown target: {target}")

async def test_target(config: Dict[str, Any], target: str):
    """Test a specific target with dry run"""
    print(f"Testing {target} in dry-run mode...")
    return await run_target(config, target, dry_run=True)

def export_results(results: Any, format: str, output_path: str):
    """Export results to specified format"""
    if format == 'csv':
        # Implementation depends on result structure
        print(f"Exporting results to CSV: {output_path}")
        # Add CSV export logic here
    elif format == 'json':
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Exporting results to JSON: {output_path}")
    elif format == 'sqlite':
        print(f"Exporting results to SQLite: {output_path}")
        # Add SQLite export logic here
    else:
        raise ValueError(f"Unsupported export format: {format}")

async def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Set up signal handlers for graceful shutdown
    setup_signal_handlers()
    
    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Failed to load configuration: {str(e)}")
        sys.exit(1)
    
    # Set up logging
    if args.debug:
        config.setdefault('logging', {})['level'] = 'DEBUG'
    elif args.verbose:
        config.setdefault('logging', {})['level'] = 'INFO'
    
    setup_logging(config)
    
    # Execute command
    if args.command == 'run':
        if not args.target:
            print("Error: --target is required for 'run' command")
            sys.exit(1)
        
        # Run in daemon mode if specified
        if args.daemon:
            print("Running in daemon mode. Press Ctrl+C to stop.")
            while True:
                try:
                    results = await run_target(config, args.target, args.dry_run)
                    if not args.once:  # In daemon mode, but --once overrides
                        # Add delay before next run
                        import asyncio
                        await asyncio.sleep(60)  # Wait 1 minute
                except KeyboardInterrupt:
                    print("Daemon stopped by user.")
                    break
        else:
            # Run once
            results = await run_target(config, args.target, args.dry_run)
            return results
    
    elif args.command == 'test-target':
        if not args.target:
            print("Error: --target is required for 'test-target' command")
            sys.exit(1)
        
        results = await test_target(config, args.target)
        return results
    
    elif args.command == 'export':
        if not args.format:
            print("Error: --format is required for 'export' command")
            sys.exit(1)
        
        print("Export command requires previous results to export.")
        # This would typically be implemented to export stored data
        # For now, we'll just show the intended functionality
        print(f"Would export data in {args.format} format")
        return []

if __name__ == '__main__':
    results = asyncio.run(main())