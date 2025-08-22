# scrape_world_capitals.py
import re
import scrapy
from scrapy.crawler import CrawlerProcess


class WorldCapitalsSpider(scrapy.Spider):
    name = "world_capitals"
    start_urls = ["https://en.wikipedia.org/wiki/List_of_national_capitals"]

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0",
        "FEEDS": {
            "world_capitals.csv": {"format": "csv", "overwrite": True, "encoding": "utf8"}
        },
        "LOG_LEVEL": "INFO",
    }

    def clean(self, texts):
        txt = " ".join(t.strip() for t in texts if t.strip())
        txt = re.sub(r"\[[^\]]*\]", "", txt)  # remove [1], [note]
        return txt.strip()

    def parse(self, response):
        for table in response.css("table.wikitable"):
            for row in table.css("tr")[1:]:
                cells = row.css("th, td")
                if len(cells) < 2:
                    continue

                country = self.clean(cells[0].css("::text").getall())
                capital = self.clean(cells[1].css("::text").getall())

                if country and capital and capital not in {"—", "-"}:
                    yield {"country_or_territory": country, "capital": capital}


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(WorldCapitalsSpider)
    process.start()
