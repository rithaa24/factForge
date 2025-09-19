"""
Items for factforge_crawler project
"""
import scrapy
from scrapy import Field

class CrawledItem(scrapy.Item):
    url = Field()
    domain = Field()
    title = Field()
    text = Field()
    html_content = Field()
    html_path = Field()
    screenshot_path = Field()
    images = Field()
    meta_tags = Field()
    headers = Field()
    crawl_timestamp = Field()
    status_code = Field()
    response_time = Field()
