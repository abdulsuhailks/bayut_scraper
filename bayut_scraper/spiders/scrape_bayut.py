import scrapy
from bayut_scraper.items import BayutItem


class BayutSpider(scrapy.Spider):
    name = "bayut_spider"
    allowed_domains = ["bayut.com"]
    start_urls = ["https://www.bayut.com/to-rent/property/dubai/"]

    def parse(self, response):
        property_links = response.xpath('//a[contains(@href, "/property/details-")]/@href').getall()
        for link in property_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_property)

        # Follow next page (pagination)
        next_page = response.xpath('//a[@aria-label="Next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_property(self, response):
        def extract(xpath):
            value = response.xpath(xpath).get()
            return value.strip() if value else ""

        def extract_list(xpath):
            return [v.strip() for v in response.xpath(xpath).getall() if v.strip()]

        item = BayutItem()

        # Property ID
        item['property_id'] = extract('//span[contains(text(), "Bayut -")]/text()')

        # URL
        item['property_url'] = response.url

        # Purpose, Type, Added On, Furnishing, Permit No.
        item['purpose'] = extract('//span[@aria-label="Purpose"]/text()'),
        item['type'] = extract('//span[@aria-label="Type"]/text()'),
        item['added_on'] = extract('//span[@aria-label="Reactivated date"]/text()'),
        item['furnishing'] = extract('//span[@aria-label="Furnishing"]/text()'),
        # item['permit_number'] = extract('//span[@aria-label="Purpose"]/text()'),

        # Agent name
        item['agent_name'] = extract('//a[@aria-label="Agent name"]/text()'),

        # Price
        item['price'] = {
            "currency": "AED",
            "amount": extract('//span[@aria-label="Price"]/text()')
        }

        # Location
        item['location'] = extract('//div[@aria-label="Property header"]/text()')

        # Bedrooms, Bathrooms, Size
        item['bed_bath_size'] = {
            "bedrooms": extract('//span[@aria-label="Beds"]/text()'),
            "bathrooms": extract('//span[@aria-label="Baths"]/text()'),
            "size": extract('//span[@aria-label="Area"]//text()')
        }

        # Breadcrumbs
        item['breadcrumbs'] = ' > '.join(extract_list('//ol[@aria-label="Breadcrumb"]/li/a/text()'))

        # Amenities
        item['amenities'] = extract_list('//div[@aria-label="Amenities"]/ul/li/text()')

        # Description
        description = extract_list('//div[@aria-label="Property description"]//text()')
        item['description'] = ' '.join(description)

        # Primary image
        item['primary_image_url'] = extract('(//img[contains(@alt, "Property image") or contains(@src, "thumbnails")])[1]/@src')

        # All property images
        item['property_image_urls'] = extract_list('//div[@aria-label="Gallery"]//img/@src')

        yield item
