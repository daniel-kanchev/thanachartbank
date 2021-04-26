import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from thanachartbank.items import Article


class thanachartbankSpider(scrapy.Spider):
    name = 'thanachartbank'
    start_urls = ['https://www.thanachartbank.co.th/TbankCMSFrontend/promotionTH.aspx?typeid=13']

    def parse(self, response):
        links = response.xpath('//table[@id="ctl00_cph1_gvPromotion"]//a[@class="linknormal"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//span[contains(@id, "PageName")]/span/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[contains(@id, "Date")]/span/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//span[contains(@id, "Content")]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
