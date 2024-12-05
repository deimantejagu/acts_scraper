# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import hashlib

from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline

class WebscraperPipeline:
    def process_item(self, item, spider):
        return item
    
class DocxFilePipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        file_url_hash = hashlib.shake_256(request.url.encode()).hexdigest(5)
        file_perspective = request.url.split("/")[-2]
        filename = f"{file_url_hash}_{file_perspective}.docx"

        return filename
