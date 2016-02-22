# PatentSlurp
Patent slurper for Dr Lars Hass, LUMS

# TODO


1) Add stripper for redundant xml tags
2) Harvest below data from Google dumps 2001-2015:
-------------------------------------------------------------------------------
              storage  display     value
variable name   type   format      label      variable label
-------------------------------------------------------------------------------
sta             str2   %2s                    assg/state
cnt             str3   %3s                    assg/country
assgnum         byte   %8.0g                  assg/assignee seq. number (imc)
cty             str72  %72s                   assg/city
pdpass          long   %12.0g                 Unique assignee number
ptype           str1   %9s                    patent type
patnum          long   %12.0g                 patent number
-------------------------------------------------------------------------------
3) Compare data with NBER data (http://eml.berkeley.edu/~bhhall/NBER06.html)
4) ...

# Useful Tools

http://codebeautify.org/xmlviewer
http://www.regexr.com/
