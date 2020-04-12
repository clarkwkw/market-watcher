from .amazon_jp import AmazonJPCrawler

all_crawlers = [AmazonJPCrawler]
all_crawlers_map = {c.platform: c for c in all_crawlers}
