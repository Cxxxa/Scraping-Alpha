#!/usr/bin/perl

use 5.010;
use strict;
use warnings;
use XML::Simple;
use XML::Twig;
use Time::Piece;

my $filename = $ARGV[0];

# Reprints only the following values from each entry in the .xml file:
# 	- application date
#	- application number
#	- publication date
#	- publication number
my $twig = new XML::Twig(TwigRoots => {'application-reference/document-id/date' => 1,
				       'application-reference/document-id/doc-number' => 2, 
				       'publication-reference/document-id/date' => 3,
				       'publication-reference/document-id/doc-number' => 4},
			 TwigHandlers => {'application-reference/document-id/date' => sub { $_->set_tag( 'application-date') },
					  'application-reference/document-id/doc-number' => sub { $_->set_tag( 'application-number') }, 
					  'publication-reference/document-id/date' => sub { $_->set_tag( 'publication-date') },
					  'publication-reference/document-id/doc-number' => sub { $_->set_tag( 'publication-number') }},
			 pretty_print => 'indented');
			 

my $numLines = countFile($filename);
print "Processing $numLines lines...\n";
processFile($filename, $numLines);
print "File processing finished - press '1' to generate SQL statements, or '0' to quit.\n";
while (1) {
   given (<STDIN>) {
      when(1) { 
	 generateSQL($filename); 
	 print "SQL generation finished.\n";
	 exit 0;
      }
      when(0) { exit 0; }
      default { print "Press '1' to generate SQL statements, or '0' to quit.\n"; }
   };
}

sub countFile {
   my $lineNum = 0;
   open(INFILE, $_[0].".xml") or die "Can't open ".$_[0].": $!";
   foreach(<INFILE>) {
      ++$lineNum;
   }
   close(INFILE);
   return $lineNum;
}

sub processFile {
   my $buffer = "";
   my $firstItem = 1;
   my $currentLine = 1;
   open(INFILE, $_[0].".xml") or die "Can't open ".$_[0].": $!";
   open(my $finalFile, ">".$_[0]."FINAL.xml") or die "Can't clear FINAL ".$_[0].": $!";
   print $finalFile "";
   close($finalFile);
   open(my $finalFile, ">>".$_[0]."FINAL.xml") or die "Can't output FINAL ".$_[0].": $!";
   print$finalFile "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<patents>\n";
   foreach(<INFILE>) {
      print "Processing line ".$currentLine."/".$_[1]."...\n";
      ++$currentLine;
      my($line) = $_;
      if ($line !~ /^\<\?xml/ && $firstItem == 0) {
	 if ($line !~ /^\<\!DOCTYPE/) {
	    $buffer = $buffer.$line;
	 }
      } else {
	 if ($firstItem == 1) {
	    $firstItem = 0;
	 } else {
	    $twig->parse($buffer);
	    $twig->print($finalFile);
	    
	    $buffer = "";
	 }
      }
   }
   print $finalFile "</patents>";
   close($finalFile);
   close(INFILE);
}

sub generateSQL {
   my $xml = new XML::Simple (KeyAttr=>[]);

   # read XML file
   my $data = $xml->XMLin($_[0]."FINAL.xml");
   
   open(my $sqlFile, ">".$_[0]."SQL.xml") or die "Can't output SQL ".$_[0].": $!";
   print $sqlFile "";
   close($sqlFile);
   
   open(my $sqlFile, ">>".$_[0]."SQL.xml") or die "Can't output SQL ".$_[0].": $!";
   print $sqlFile "CREATE TABLE IF NOT EXISTS `patents`\n(\n\t`pid` INT NOT NULL AUTO_INCREMENT,\n\tPRIMARY KEY(`pid`),\n\t`pubNum` VARCHAR(32),\n\t`pubDate` DATETIME,\n\t`appNum` VARCHAR(32),\n\t`appDate` DATETIME\n);\n\n";
   foreach my $e (@{$data->{'us-patent-grant'}}) {
      print $sqlFile "INSERT INTO `patents`(`pubNum`, `pubDate`, `appNum`, `appDate`) VALUES ('".$e->{'publication-number'}."', '".$e->{'publication-date'}."', '".$e->{'application-number'}."', '".$e->{'application-date'}."');\n";
   }
   close($sqlFile);
}
