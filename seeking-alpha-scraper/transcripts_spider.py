import scrapy
import re

class TranscriptSpider(scrapy.Spider):
    name = 'transcripts'

    start_urls = ['http://seekingalpha.com/earnings/earnings-call-transcripts/1']
    def cleanhtml(raw_html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext
	
    def parse(self, response):
        # follow links to transcript pages
        for href in response.css('.dashboard-article-link::attr(href)').extract():
            yield scrapy.Request(response.urljoin(href),
                                 callback=self.parse_transcript)

        # follow pagination links
        #next_page = response.css('li.next a::attr(href)').extract_first()
        #if next_page is not None:
        #    next_page = response.urljoin(next_page)
        #    yield scrapy.Request(next_page, callback=self.parse)
    
    def parse_transcript(self, response):
	i = 4
        def extract_with_css(query):
            return response.css(query).extract_first().strip()
	
	body = response.css('div#a-body p.p1')
	chunks = body.css('p.p1')
	firstline = chunks[0].css('p::text').extract()
	ticker = chunks.css('a::text').extract_first()
	if ":" in ticker: 
	    ticker = ticker.split(':')[1]
	
	name = re.compile('([A-z -]* - [A-z ,&-]*)')
	execs = []
	analysts = []
	
	nextLine = chunks[i].css('p::text').extract_first()
	while re.match(name, nextLine) is not None:
	    execs.append(nextLine)
	    i += i
	    nextLine = chunks[i].css('p::text').extract_first()
	print "DONE EXECS"
	print i
	print "Next line: "+nextLine
	while re.match(name, nextLine) is not None:
	    analysts.append(nextLine)
	    i += i
	    nextLine = chunks[i].css('p::text').extract_first()
	print "DONE ANALYSTS"
	
	print execs
	print "-----------"
	print analysts
	print "^^^^^^^^^"
	
	#### PLACEHOLDER
	i = 0
	while True:
	    print i ,": " , chunks[i].css('p::text').extract_first()
	    print i ,": " , chunks[i].css('strong::text').extract_first()
	    i += 1
	    
        #yield {
	#    'company': firstline[0].split(" (", 1)[0],
         #   'stockmarket': firstline[0].split(" (", 1)[1],
	 #   'ticker': ticker,
	#    'title': chunks[1].css('p::text').extract_first(),
	#    'date': chunks[2].css('p::text').extract_first()
        #}
