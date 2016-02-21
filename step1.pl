#!/usr/bin/perl

use 5.010;
use strict;
use warnings;

my($filename) = @ARGV;

my $linesNum = 0;
open(FILE, $filename) or die "Can't open `$filename': $!";
while (sysread FILE, $buffer, 4096) {
   $linesNum += ($buffer =~ tr/\n//);
}
close FILE;
open(MYOUTFILE, ">".$filename."CLEAN.xml");
print MYOUTFILE "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE us-patent-grant SYSTEM \"us-patent-grant-v45-2014-04-03.dtd\" [ ]>\n";
close(MYOUTFILE);

open(MYINPUTFILE, "<".$filename.".xml");
open(MYOUTFILE, ">>".$filename."CLEAN.xml");
while(<MYINPUTFILE>) {
   my($line) = $_;
   chomp($line);
   if ($line =~ /^\<\?xml/) {
      print MYOUTFILE $line;
   }
}