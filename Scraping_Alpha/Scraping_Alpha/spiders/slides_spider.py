#
#	Title: Scraping Alpha
#	Version: 1.0
#	Author: Ben Goldsworthy <b.goldsworthy@lancaster.ac.uk>
#
#	This file is a part of Scraping Alpha, a series of scripts to scrape
#	earnings call transcripts from seekingalpha.com and present them as useful
#	SQL.
#
#	This file is the webspider that Scrapy uses to retrieve slides.
#

import scrapy
urls = []
# A transcript record can be uniquely identified using it's company name + date.
uniqueID = ""
# Some transcript preambles are concatenated on a single line. This list is used
# To separate the title and date sections of the string.
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

class SlidesSpider(scrapy.Spider):
    name = 'slides'
    start_urls = ['http://seekingalpha.com/earnings/earnings-call-transcripts/1']
	
    def parse(self, response):
        # Follows each transcript page's link from the given index page.
        for href in response.css('.dashboard-article-link::attr(href)').extract():
            yield scrapy.Request(response.urljoin(href), callback=self.parse_transcript)
            
        # Follows the pagination links at the bottom of given index page.
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(next_page, callback=self.parse)
    
    def parse_transcript(self, response):
        slides = response.css('li#slides a::attr(href)').extract_first()
    	if slides is not None:
			body = response.css('div#a-body p.p1')
			chunks = body.css('p.p1')
			i = 0
			while i < 3:
				# If we're on the first line of the preamble, that's the
				# company name, stock exchange and ticker acroynm (or should
				# be - see below)
				if i == 0:
					# Checks to see if the second line is a heading. If not,
					# everything is fine.
					if len(chunks[1].css('strong::text').extract()) == 0:
						uniqueID = chunks[i].css('p::text').extract_first()
						if " (" in uniqueID:
							uniqueID = uniqueID.split(' (')[0]
						i = 2
					# However, if it is, that means this line contains the
					# full, concatenated preamble, so everything must be 
					# extracted here
					else:
						uniqueID = chunks[i].css('p::text').extract_first()
						if " (" in uniqueID:
							uniqueID = uniqueID.split(' (')[0]
						titleAndDate = chunks[i].css('p::text').extract[1]
						for date in months:
							if date in titleAndDate:
								splits = titleAndDate.split(date)
								uniqueID = uniqueID + ";" + date + splits[1]
						i = 3
				# Otherwise, we're onto the date line.
				elif i == 2:
					uniqueID = uniqueID + ";" + chunks[i].css('p::text').extract_first()
				i += 1
			
			slides = response.urljoin(slides)
			yield uniqueID
			#yield scrapy.Request(sides, callback=self.parse_slides)
			
	def parse_slides(self, response):
		urls = response.css('figure img::attr(src)').extract()
		yield uniqueID + "\\\\" + ';'.join(urls)
		
