#
#	Title: Scraping Alpha
#	Version: 1.0
#	Author: Ben Goldsworthy <b.goldsworthy@lancaster.ac.uk>
#
#	This file is a part of Scraping Alpha, a series of scripts to scrape
#	earnings call transcripts from seekingalpha.com and present them as useful
#	SQL.
#
#	This file takes the `transcripts.json` file output of `transcript_spider.py`
#	and converts it into SQL.
#	
#	This file should be located in the same directory as `transcripts.json`, and
#	is run via 'python JSONtoSQL.py > [FILE].sql', where '[FILE]' is the name of
#	the output file. 
#

import json
import sys
import codecs

sys.stdout=codecs.getwriter('utf-8')(sys.stdout)

json_data=open('transcripts.json').read()

data = json.loads(json_data)

executives = []
analysts = []

# For each transcript, creates new, separate arrays of executives and analysts
# for their own database tables, replacing their tuples in the transcript with
# their database keys.
for entry in data:
	indexExec = len(executives)+1
	indexAnal = len(analysts)+1
	
	newExecs = []
	for executive in entry['entry']['exec']:
		if executive not in executives:
			executives.append(executive)
			newExecs.append(indexExec)
			indexExec += 1
		else:
			newExecs.append(executives.index(executive) + 1)
	entry['entry']['exec'] = newExecs
	
	newAnals = []
	for analyst in entry['entry']['analysts']:
		if analyst not in analysts:
			analysts.append(analyst)
			newAnals.append(indexAnal)
			indexAnal += 1
		else:
			newAnals.append(analysts.index(analyst) + 1)
	entry['entry']['analysts'] = newAnals

# Outputs the SQL file that creates the various tables and populates them with
# INSERT statements.
print "CREATE TABLE IF NOT EXISTS `execs`"
print "("
print "\t`id` INT NOT NULL UNIQUE AUTO_INCREMENT,"
print "\t`name` VARCHAR(255),"
print "\t`position` VARCHAR(255),"
print "\t`company` VARCHAR(255),"
print "\tPRIMARY KEY(`id`)"
print ");\n"

print "INSERT INTO `execs` (`name`, `position`, `company`) VALUES"
print "\t(0,0,0)",
for executive in executives:
	print ","
	print "\t(\""+executive[0]+"\",\""+executive[1]+"\",\""+executive[2]+"\")",
print ";\n"

print "CREATE TABLE IF NOT EXISTS `analysts`"
print "("
print "\t`id` INT NOT NULL UNIQUE AUTO_INCREMENT,"
print "\t`name` VARCHAR(255),"
print "\t`company` VARCHAR(255),"
print "\tPRIMARY KEY(`id`)"
print ");\n"

print "INSERT INTO `analysts` (`name`, `company`) VALUES"
print "\t(0,0)",
for analyst in analysts:
	print ","
	print "\t(\""+analyst[0]+"\",\""+analyst[1]+"\")",
print ";\n"

print "CREATE TABLE IF NOT EXISTS `transcripts`"
print "("
print "\t`id` INT NOT NULL UNIQUE AUTO_INCREMENT,"
print "\t`title` VARCHAR(255),"
print "\t`company` VARCHAR(255),"
print "\t`execs` VARCHAR(255),"
print "\t`analysts` VARCHAR(255),"
print "\t`transcript` TEXT,"
print "\tPRIMARY KEY(`id`)"
print ");\n"

print "INSERT INTO `transcripts` (`title`, `company`, `execs`, `analysts`, `transcript`) VALUES"
print "\t(0,0,0,0,0)",
for entry in data:
	tran = entry['entry']
	print ","
	print "\t(\""+tran['title']+"\",\""+tran['company']+"\",\""+(';'.join(str(x) for x in tran['exec']))+"\",\""+(';'.join(str(x) for x in tran['analysts']))+"\",\""+tran['transcript']+"\")",
print ";\n"

print "CREATE TABLE IF NOT EXISTS `execs_to_transcripts`"
print "("
print "\t`exec_id` INT NOT NULL,"
print "\t`transcript_id` INT NOT NULL,"
print "\tPRIMARY KEY(`exec_id`, `transcript_id`),"
print "\tFOREIGN KEY (`exec_id`) REFERENCES `execs`(`id`),"
print "\tFOREIGN KEY (`transcript_id`) REFERENCES `transcripts`(`id`)"
print ");\n"

print "CREATE TABLE IF NOT EXISTS `analysts_to_transcripts`"
print "("
print "\t`analyst_id` INT NOT NULL,"
print "\t`transcript_id` INT NOT NULL,"
print "\tPRIMARY KEY(`analyst_id`, `transcript_id`),"
print "\tFOREIGN KEY (`analyst_id`) REFERENCES `analysts`(`id`),"
print "\tFOREIGN KEY (`transcript_id`) REFERENCES `transcripts`(`id`)"
print ");"
