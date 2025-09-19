"""
Scrapy settings for factforge_crawler project
"""
import os

BOT_NAME = 'factforge_crawler'

SPIDER_MODULES = ['factforge_crawler.spiders']
NEWSPIDER_MODULE = 'factforge_crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure delays
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# Configure concurrent requests
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Configure user agent
USER_AGENT = 'FactForge-Crawler/1.0 (+https://factforge.com/bot)'

# Configure pipelines
ITEM_PIPELINES = {
    'factforge_crawler.pipelines.RabbitMQPipeline': 300,
}

# Configure middlewares
DOWNLOADER_MIDDLEWARES = {
    'factforge_crawler.middlewares.RotateUserAgentMiddleware': 400,
    'factforge_crawler.middlewares.ProxyMiddleware': 410,
}

# Configure request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Configure response encoding
FEED_EXPORT_ENCODING = 'utf-8'

# Configure logging
LOG_LEVEL = 'INFO'

# Configure autothrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Configure caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'

# Configure retry
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Configure timeout
DOWNLOAD_TIMEOUT = 30

# Configure headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en,hi,ta,kn',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# RabbitMQ settings
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

# Data storage settings
DATA_DIR = os.getenv('DATA_DIR', '/app/data')
RAW_HTML_DIR = os.path.join(DATA_DIR, 'raw')
SCREENSHOTS_DIR = os.path.join(DATA_DIR, 'screenshots')

# Ensure directories exist
os.makedirs(RAW_HTML_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
