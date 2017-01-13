# Scraping Alpha

## Author

Ben Goldsworthy
<[email](mailto:b.goldsworthy@lancaster.ac.uk)> 
<[website](http://www.bengoldsworthy.uk/)>

## Version

1.0

## Abstract

Scraping Alpha is a series of Python scripts used to scrape 
[Seeking Alpha](http://seekingalpha.com/) earnings call transcripts and produce 
SQL from them.

It was created for Dr Lars Hass of the Lancaster University Management School.

## Usage

The instructions for each step of the process can be found at the beginning of 
each of the files involved: `transcript_spider.py`, `JSONtoSQL.py` and 
`execsAndAnalysts.py`. The are repeated here for brevity.

### `transcript_spider.py`

This file is the webspider that Scrapy uses to retrieve the information from the
 website. Left unattended, it will scrape all 4,000+ pages of results.
To interrupt this behaviour and still be able to proceed with the other steps, 
cancel the script with `CTRL+Z`. This will likely leave an unfinished JSON item 
at the end of the output file. To clear this up, open the file in `vim` and type
 the following keys: 
```vim
G
V
d
$
i
BACKSPACE
ENTER
]
ESC
:wp
ENTER
```

This will truncate the file at the last complete record and seal it off.

For installation instructions for Scrapy, see 
[here](https://doc.scrapy.org/en/latest/intro/install.html). This file should be
 in the `spiders` directory of the project, and is run via `scrapy crawl 
 transcripts -o transcripts.json` at the command line (the output file will be 
 placed in the directory the Terminal is currently pointing to).

### `JSONtoSQL.py`

This file takes the `transcripts.json` file output of `transcript_spider.py` and
 converts it into SQL.

This file should be located in the same directory as `transcripts.json`, and is 
run via `python JSONtoSQL.py > [FILE].sql`, where `[FILE]` is the desired name 
of the output file. 

### `execsAndAnalysts.py`

First, import the output file of `JSONtoSQL.py` to your chosen DBMS (I've tested
 it with phpMyAdmin). Then, run the following query:
```SQL
SELECT `id`, `execs`, `analysts` FROM `transcripts`
```

Export the resulting table ([instructions](http://serverfault.com/a/435443)) to 
`transcripts.sql`, and place the file in the same directory as 
`execsAndAnalysts.py`. Run it with 'python execsAndAnalysts'.

It creates from this two files (`execs.sql` and `analysts.sql`). Import them 
into your DBMS to create two linking tables. The final instruction of 
`analysts.sql` then deletes the superfluous `execs` and `analysts` columns from 
the `transcripts` table (and for this reason, `execs.sql` must be imported first).

## Future

Harvesting the URLs of slide images shouldn't be too hard to implement - `slides_spider.py` should in theory to this, but the link to a transcript's slides is added to the page later via Javascript, which means at the moment it throws up a load of HTTP 200 status codes and nowt else. [Scrapy+Splash](https://github.com/scrapy-plugins/scrapy-splash) may be the solution, however.
