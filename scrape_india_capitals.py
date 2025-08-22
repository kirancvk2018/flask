# scrape_india_capitals.py
import re
import scrapy
from scrapy.crawler import CrawlerProcess


class IndiaCapitalsSpider(scrapy.Spider):
    name = "india_capitals"

    def __init__(self, url=None, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [
            url
            or "https://en.wikipedia.org/wiki/List_of_state_and_union_territory_capitals_in_India"
        ]

    # Scrapy settings for this one-file spider
    custom_settings = {
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.25,
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            "india_capitals.csv": {"format": "csv", "overwrite": True},
        },
    }

    @staticmethod
    def _clean(text_list):
        """Join text nodes, strip whitespace, remove citation brackets like [1], [note 2]."""
        txt = " ".join(t.strip() for t in text_list if t and t.strip())
        txt = re.sub(r"\[[^\]]*\]", "", txt)     # remove [ ... ]
        txt = re.sub(r"\s+", " ", txt)           # collapse whitespace
        return txt.strip()

    def parse(self, response):
        # Use the first wikitable on the page
        rows = response.css("table.wikitable tbody tr")
        if not rows:
            self.logger.warning("No table.wikitable found.")
            return

        for row in rows[1:]:  # skip header
            tds = row.css("td")
            if len(tds) < 2:
                continue

            state_ut = self._clean(tds[0].css("::text").getall())
            capital = self._clean(tds[1].css("::text").getall())

            if state_ut and capital:
                # write to feed (CSV) via yield
                yield {"state_or_ut": state_ut, "capital": capital}
                # also print to console (fixed variable name)
                print(f"State/UT: {state_ut:30}  Capital: {capital}")


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(IndiaCapitalsSpider)
    process.start()
