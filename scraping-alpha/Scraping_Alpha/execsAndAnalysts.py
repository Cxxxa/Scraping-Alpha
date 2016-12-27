#
#	Title: Scraping Alpha
#	Version: 1.0
#	Author: Ben Goldsworthy <b.goldsworthy@lancaster.ac.uk>
#
#	This file is a part of Scraping Alpha, a series of scripts to scrape
#	earnings call transcripts from seekingalpha.com and present them as useful
#	SQL.
#
#	This file takes the `transcripts.sql` file exported from the database
# 	created using the output file of `JSONtoSQL.py` after the following query:
#		SELECT `id`, `execs`, `analysts` FROM `transcripts`
#	It creates from this two `execs.sql` and `analysts.sql` for creating linking
#	tables in the database.
#	
#	This file should be located in the same directory as `transcripts.sql`, and
#	is run via 'python execsAndAnalysts'.
#

import sys
import codecs
import os
from shutil import copyfile
import fileinput

sys.stdout=codecs.getwriter('utf-8')(sys.stdout)

start = 0

# Creates a temporary copy in case something goes Pete Tong.
copyfile("transcripts.sql", "transcripts.sql.tmp")

# Trims everything from the export except for the INSERT statement.
for line in fileinput.FileInput("transcripts.sql.tmp",inplace=1):
	if start == 0:
		if "INSERT INTO `transcripts`" in line:
			start = 1
			print "INSERT INTO `execs_to_transcripts` (`exec_id`, `transcript_id`) VALUES"
	else:
		if line == "\n":
			start = 0
		else:
			print "\t"+line,

# Copies the produced file to create both the output files, then deletes the
# temporary file.
copyfile("transcripts.sql.tmp", "execs.sql")
copyfile("transcripts.sql.tmp", "analysts.sql")
os.remove("transcripts.sql.tmp")

# Converts each line "(x, '0;...;n')" in the file to n separate INSERTs, one
# for each executive.
start = 0
nL = ""
for line in fileinput.FileInput("execs.sql",inplace=1):
	if start == 0:
		start = 1
	else:
		bits = line.split(', ')
		tID = bits[0].strip('\t').strip('(')
		execs = bits[1].split(';')
		newLines = ""
		for execID in execs:
			newLines = newLines + nL + "\t("+tID+", "+execID.strip('\'')+"),"
		line = line.replace(line, newLines)
		nL = "\n"
	print line,
	
# Does the same for the analysts.
start = 0
nL = ""
for line in fileinput.FileInput("analysts.sql",inplace=1):
	if start == 0:
		start = 1
		line = line.replace(line, "INSERT INTO `analysts_to_transcripts` (`analyst_id`, `transcript_id`) VALUES\n")
	else:
		bits = line.split(', ')
		tID = bits[0].strip('\t').strip('(')
		# As it is possible for there to be no analysts in a call, this ignores
		# blank results.
		if "''" not in bits[2]:
			analysts = bits[2].split(';')
			newLines = ""
			for analystID in analysts:
				# This stops the final transcript from getting an additional, 
				# `analyst_id`-less INSERT
				if analystID != '\n':
					newLines = newLines + nL + "\t("+tID+", "+analystID.strip('\'').strip('\'),\n')+"),"
			line = line.replace(line, newLines)
			nL = "\n"
		else:
			line = ""
	print line,
	
# Replace the final comma at the end of each file with a semicolon, to make it
# valid SQL
with open("execs.sql", 'rb+') as filehandle:
    filehandle.seek(-1, os.SEEK_END)
    filehandle.truncate()
    filehandle.write(";")
with open("analysts.sql", 'rb+') as filehandle:
    filehandle.seek(-1, os.SEEK_END)
    filehandle.truncate()
    filehandle.write(";")
    # `analysts.sql` then performs some cleanup on the database.
    filehandle.write("\n\nALTER TABLE `transcripts`\n\tDROP COLUMN `execs`,\n\tDROP COLUMN `analysts`;\n\n")
    filehandle.write("DELETE FROM `transcripts` WHERE `id` = 0;\n")
    filehandle.write("DELETE FROM `execs` WHERE `id` = 0;\n")
    filehandle.write("DELETE FROM `analysts` WHERE `id` = 0;\n")
    filehandle.write("DELETE FROM `execs_to_transcripts` WHERE `transcript_id` = 0;\n")
    filehandle.write("DELETE FROM `analysts_to_transcripts` WHERE `transcript_id` = 0;\n")
