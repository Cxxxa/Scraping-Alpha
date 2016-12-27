#-*- coding: utf-8 -*-

#	Title: Scraping Alpha
#	Version: 1.0
#	Author: Ben Goldsworthy <b.goldsworthy@lancaster.ac.uk>
#
#	This file is a part of Scraping Alpha, a series of scripts to scrape
#	earnings call transcripts from seekingalpha.com and present them as useful
#	SQL.
#
#	This file is the webspider that Scrapy uses to retrieve the information from
#	the website. Left unattended, it will scrape all 4,000+ pages of results.
#	
#	To interrupt this behaviour and still be able to proceed with the other
#	steps, cancel the script with CTRL+Z. This will likely leave an unfinished
#	JSON item at the end of the output file. To clear this up, open the file
#	in vim and type the following keys: 
#		'G', 'V', 'd', '$', 'i', 'BACKSPACE', 'ENTER', ']', 'ESC', ':wp', 'ENTER'
#	This will truncate the file at the last complete record and seal it off.
#
# 	For installation instructions for Scrapy, visit 
# 	<doc.scrapy.org/en/latest/intro/install.html>. This file should be in the
# 	`spiders` directory of the project, and is run via 'scrapy crawl transcripts 
# 	-o transcripts.json' at the command line (the output file will be placed
#	in the directory the Terminal is currently in).
#

import scrapy
# This enum lists the stages of each transcript.
from enum import Enum
Stage = Enum('Stage', 'preamble execs analysts body')
# Some transcript preambles are concatenated on a single line. This list is used
# To separate the title and date sections of the string.
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
transcripts = {}

class TranscriptSpider(scrapy.Spider):
    name = 'transcripts'
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
		i = 0
		transcript = {}
		details = {}
		execs = []
		analysts = []
		script = []
		mode = 1
		
		# As the pages are represented by a series of `<p>` elements, all with
		# the same class `.p1` and no unique identfiers, we have to do this the
		# old-fashioned way - breaking it into chunks and iterating over them.
		body = response.css('div#a-body p.p1')
		chunks = body.css('p.p1')
		while i < len(chunks):
			# If the current line is a heading and we're not currently going
			# through the transcript body (where headings represent speakers),
			# change the current section flag to the next section.
			if (len(chunks[i].css('strong::text').extract()) == 0) or (mode == 4):
				currStage = Stage(mode)
				# If we're on the preamble stage, each bit of data is extracted
				# separately as they all have their own key in the JSON.
				if currStage == Stage['preamble']:
					# If we're on the first line of the preamble, that's the
					# company name, stock exchange and ticker acroynm (or should
					# be - see below)
					if i == 0:
						# Checks to see if the second line is a heading. If not,
						# everything is fine.
						if len(chunks[1].css('strong::text').extract()) == 0:
							details['company'] = chunks[i].css('p::text').extract_first()
							if " (" in details['company']:
								details['company'] = details['company'].split(' (')[0]
							# If a specific stock exchange is not listed, it
							# defaults to NYSE
							details['exchange'] = "NYSE"
							details['ticker'] = chunks.css('a::text').extract_first()
							if ":" in details['ticker']:
								ticker = details['ticker'].split(':')
								details['exchange'] = ticker[0]
								details['ticker'] = ticker[1]
						# However, if it is, that means this line contains the
						# full, concatenated preamble, so everything must be 
						# extracted here
						else:
							details['company'] = chunks[i].css('p::text').extract_first()
							if " (" in details['company']:
								details['company'] = details['company'].split(' (')[0]
							# if a specific stock exchange is not listed, default to NYSE
							details['exchange'] = "NYSE"
							details['ticker'] = chunks.css('a::text').extract_first()
							if ":" in details['ticker']:
								ticker = details['ticker'].split(':')
								details['exchange'] = ticker[0]
								details['ticker'] = ticker[1]
							titleAndDate = chunks[i].css('p::text').extract[1]
							for date in months:
								if date in titleAndDate:
									splits = titleAndDate.split(date)
									details['title'] = splits[0]
									details['date'] = date + splits[1]
					# Otherwise, we're onto the title line.
					elif i == 1:
						title = chunks[i].css('p::text').extract_first()
						# This should never be the case, but just to be careful
						# I'm leaving it in.
						if len(title) <= 0:
							title = "NO TITLE"
						details['title'] = title
					# Or the date line.
					elif i == 2:
						details['date'] = chunks[i].css('p::text').extract_first()
				# If we're onto the 'Executives' section, we create a list of
				# all of their names, positions and company name (from the 
				# preamble).
				elif currStage == Stage['execs']:					
					anExec = chunks[i].css('p::text').extract_first().split(" - ")
					# This covers if the execs are separated with an em- rather
					# than an en-dash (see above).
					if len(anExec) <= 1:
						anExec = chunks[i].css('p::text').extract_first().split(" – ")
					name = anExec[0]
					if len(anExec) > 1:
						position = anExec[1]
					# Again, this should never be the case, as an Exec-less
					# company would find it hard to get much done.
					else:
						position = ""
					execs.append((name,position,details['company']))
				# This does the same, but with the analysts (which never seem
				# to be separated by em-dashes for some reason).
				elif currStage == Stage['analysts']:
					name = chunks[i].css('p::text').extract_first().split(" - ")[0]
					company = chunks[i].css('p::text').extract_first().split(" - ")[1]
					analysts.append((name,company))
				# This strips the transcript body of everything except simple
				# HTML, and stores that.
				elif currStage == Stage['body']:
					line = chunks[i].css('p::text').extract_first()
					html = "p>"
					if line is None:
						line = chunks[i].css('strong::text').extract_first()
						html = "h1>"
					script.append("<"+html+line+"</"+html)
			else:
				mode += 1
			i += 1
		
		# Adds the various arrays to the dictionary for the transcript
		details['exec'] = execs 
		details['analysts'] = analysts
		details['transcript'] = ''.join(script)
		
		# Adds this transcript to the dictionary of all scraped
		# transcripts, and yield that for the output
		transcript["entry"] = details
		yield transcript
