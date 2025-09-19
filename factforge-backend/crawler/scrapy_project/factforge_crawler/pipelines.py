"""
Pipelines for factforge_crawler project
"""
import os
import json
import hashlib
import pika
from urllib.parse import urlparse
from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
from scrapy.exceptions import DropItem
import logging

logger = logging.getLogger(__name__)

class RabbitMQPipeline:
    """Pipeline to send items to RabbitMQ"""
    
    def __init__(self):
        self.rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
        self.connection = None
        self.channel = None
    
    def open_spider(self, spider):
        """Open spider - establish RabbitMQ connection"""
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='crawl.items', durable=True)
            logger.info("RabbitMQ connection established")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
    
    def close_spider(self, spider):
        """Close spider - close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")
    
    def process_item(self, item, spider):
        """Process item - send to RabbitMQ"""
        try:
            # Convert item to dict
            item_dict = dict(item)
            
            # Send to RabbitMQ
            message = json.dumps(item_dict)
            self.channel.basic_publish(
                exchange='',
                routing_key='crawl.items',
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
            )
            
            logger.info(f"Sent item to RabbitMQ: {item['url']}")
            return item
            
        except Exception as e:
            logger.error(f"Failed to send item to RabbitMQ: {e}")
            raise DropItem(f"RabbitMQ error: {e}")

class ScreenshotPipeline(ImagesPipeline):
    """Pipeline to capture screenshots using Playwright"""
    
    def __init__(self, store_uri, download_func=None, settings=None):
        super().__init__(store_uri, download_func, settings)
        self.screenshots_dir = os.getenv('SCREENSHOTS_DIR', '/app/data/screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def get_media_requests(self, item, info):
        """Generate screenshot request"""
        return [Request(item['url'], meta={'item': item})]
    
    def item_completed(self, results, item, info):
        """Process completed screenshot"""
        if results:
            for success, result in results:
                if success:
                    item['screenshot_path'] = result['path']
                else:
                    item['screenshot_path'] = None
        return item
    
    def media_downloaded(self, request, response):
        """Download and process screenshot"""
        try:
            # Use Playwright to capture screenshot
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set viewport size
                page.set_viewport_size({"width": 1920, "height": 1080})
                
                # Navigate to page
                page.goto(request.url, timeout=30000)
                
                # Wait for page to load
                page.wait_for_load_state("networkidle")
                
                # Generate filename
                url_hash = hashlib.md5(request.url.encode()).hexdigest()
                filename = f"{url_hash}.png"
                filepath = os.path.join(self.screenshots_dir, filename)
                
                # Capture screenshot
                page.screenshot(path=filepath, full_page=True)
                
                browser.close()
                
                return {
                    'path': filepath,
                    'checksum': hashlib.md5(open(filepath, 'rb').read()).hexdigest()
                }
                
        except Exception as e:
            logger.error(f"Screenshot capture failed for {request.url}: {e}")
            return None

class HTMLStoragePipeline:
    """Pipeline to store raw HTML content"""
    
    def __init__(self):
        self.html_dir = os.getenv('RAW_HTML_DIR', '/app/data/raw')
        os.makedirs(self.html_dir, exist_ok=True)
    
    def process_item(self, item, spider):
        """Store HTML content to file"""
        try:
            if 'html_content' in item and item['html_content']:
                # Generate filename
                url_hash = hashlib.md5(item['url'].encode()).hexdigest()
                filename = f"{url_hash}.html"
                filepath = os.path.join(self.html_dir, filename)
                
                # Write HTML content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(item['html_content'])
                
                item['html_path'] = filepath
                logger.info(f"Stored HTML: {filepath}")
            
            return item
            
        except Exception as e:
            logger.error(f"HTML storage failed: {e}")
            return item

class DuplicateFilterPipeline:
    """Pipeline to filter duplicate URLs"""
    
    def __init__(self):
        self.seen_urls = set()
    
    def process_item(self, item, spider):
        """Filter duplicate URLs"""
        url = item['url']
        
        if url in self.seen_urls:
            raise DropItem(f"Duplicate URL: {url}")
        
        self.seen_urls.add(url)
        return item
