"""
Seed spider for crawling URLs from seed files
"""
import os
import scrapy
from scrapy.spiders import Spider
from factforge_crawler.items import CrawledItem
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)

class SeedSpider(Spider):
    name = 'seed_spider'
    allowed_domains = []
    
    def __init__(self, seed_file=None, *args, **kwargs):
        super(SeedSpider, self).__init__(*args, **kwargs)
        self.seed_file = seed_file or os.getenv('SEED_FILE', '/app/data/seeds/seeds.txt')
        self.start_urls = self.load_seed_urls()
    
    def load_seed_urls(self):
        """Load URLs from seed file"""
        urls = []
        
        if os.path.exists(self.seed_file):
            try:
                with open(self.seed_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        url = line.strip()
                        if url and not url.startswith('#'):
                            urls.append(url)
                logger.info(f"Loaded {len(urls)} URLs from seed file")
            except Exception as e:
                logger.error(f"Failed to load seed file: {e}")
        else:
            logger.warning(f"Seed file not found: {self.seed_file}")
            # Use default URLs for testing
            urls = [
                'https://example.com',
                'https://httpbin.org/html',
                'https://httpbin.org/json'
            ]
        
        return urls
    
    def start_requests(self):
        """Generate initial requests"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'download_timeout': 30}
            )
    
    def parse(self, response):
        """Parse response and extract data"""
        try:
            # Extract basic information
            item = CrawledItem()
            item['url'] = response.url
            item['domain'] = urlparse(response.url).netloc
            item['title'] = response.css('title::text').get()
            item['text'] = self.extract_text(response)
            item['html_content'] = response.text
            item['images'] = self.extract_images(response)
            item['meta_tags'] = self.extract_meta_tags(response)
            item['headers'] = dict(response.headers)
            item['crawl_timestamp'] = response.meta.get('download_time')
            item['status_code'] = response.status
            item['response_time'] = response.meta.get('download_latency', 0)
            
            # Extract links for further crawling
            links = self.extract_links(response)
            for link in links[:10]:  # Limit to 10 links per page
                yield scrapy.Request(
                    url=link,
                    callback=self.parse,
                    meta={'download_timeout': 30}
                )
            
            yield item
            
        except Exception as e:
            logger.error(f"Parse error for {response.url}: {e}")
    
    def extract_text(self, response):
        """Extract text content from response"""
        try:
            # Remove script and style elements
            for script in response.css('script'):
                script.extract()
            for style in response.css('style'):
                style.extract()
            
            # Extract text from all elements
            text_parts = []
            for element in response.css('*::text'):
                text = element.get().strip()
                if text:
                    text_parts.append(text)
            
            return ' '.join(text_parts)
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
    
    def extract_images(self, response):
        """Extract image URLs from response"""
        try:
            images = []
            for img in response.css('img'):
                src = img.css('::attr(src)').get()
                if src:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(response.url, src)
                    images.append(absolute_url)
            return images
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            return []
    
    def extract_meta_tags(self, response):
        """Extract meta tags from response"""
        try:
            meta_tags = {}
            for meta in response.css('meta'):
                name = meta.css('::attr(name)').get()
                content = meta.css('::attr(content)').get()
                if name and content:
                    meta_tags[name] = content
            return meta_tags
        except Exception as e:
            logger.error(f"Meta tag extraction failed: {e}")
            return {}
    
    def extract_links(self, response):
        """Extract links from response"""
        try:
            links = []
            for link in response.css('a'):
                href = link.css('::attr(href)').get()
                if href:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(response.url, href)
                    # Filter out non-HTTP URLs
                    if absolute_url.startswith(('http://', 'https://')):
                        links.append(absolute_url)
            return links
        except Exception as e:
            logger.error(f"Link extraction failed: {e}")
            return []
