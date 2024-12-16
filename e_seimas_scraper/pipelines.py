# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from scrapy.pipelines.files import FilesPipeline

class e_seimas_scraperPipeline:
    def process_item(self, item, spider):
        return item
    
class DocxFilePipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        file_perspective = request.url.split("/")[-4]
        filename = f"{file_perspective}.docx"

        return filename
