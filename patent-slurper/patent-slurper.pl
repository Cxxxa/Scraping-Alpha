#!/usr/bin/env perl

use 5.010;
#use strict;
use warnings;
use XML::Simple;
use XML::Twig;
use Time::Piece;

=pod

=head1 NAME

PATENT_SLURPER - A program to process Google/USPTO data dumps

=head1 VERSION

0.8

=head1 DESCRIPTION

This program takes L<Google/USPTO data dumps|https://www.google.com/googlebooks/uspto-patents-grants-text.html>
and produces SQL commands to generate a database from them with a 
number of selected fields.

=head1 AUTHOR

L<Ben Goldsworthy (rumperuu)|mailto:b.goldsworthy96@gmail.com>

=head1 LICENSE

=cut

# Trims the file extension from the filename argument
my $filename = $ARGV[0];
chomp  $filename;

my $patentTwig = new XML::Twig(TwigRoots => { 
                                                      'SDOBI/B100/B140/DATE/PDAT' => 1,
                                                      'SDOBI/B100/B110/DNUM/PDAT' => 2, 
                                                      'SDOBI/B200/B220/DATE/PDAT' => 3,
                                                      'SDOBI/B200/B210/DNUM/PDAT' => 4 
                                                    },
                     TwigHandlers => { 
                                          'SDOBI/B100/B140/DATE/PDAT' => sub { $_->set_tag( 'appdate') },
                                          'SDOBI/B100/B110/DNUM/PDAT' => sub { $_->set_tag( 'appnum') }, 
                                          'SDOBI/B200/B220/DATE/PDAT' => sub { $_->set_tag( 'pubdate') },
                                          'SDOBI/B200/B210/DNUM/PDAT' => sub { $_->set_tag( 'pubnum') } 
                                       },
                     pretty_print => 'indented');
my $citationTwig = new XML::Twig(TwigRoots => { 
                                                         'SDOBI/B200/B210/DNUM/PDAT' => 1,
                                                         'SDOBI/B500/B560/B561/PCIT/DOC/DNUM/PDAT' => 2
                                                     },
                      TwigHandlers => { 
                                          'SDOBI/B200/B210/DNUM/PDAT' => sub { $_->set_tag( 'pubnum') },
                                          'SDOBI/B500/B560/B561/PCIT/DOC/DNUM/PDAT' => sub { $_->set_tag('citing') }
                                         },
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
      } when(0) { 
         exit 0; 
      } default { 
         print "Press '1' to generate SQL statements, or '0' to quit.\n";
      }
   };
}

# Goes through the file serially to count the lines
sub countFile {
   my $lineNum = 0;
   open(INFILE, "data/".$_[0].".xml") or die "Can't open ".$_[0].": $!";
   foreach(<INFILE>) {
      ++$lineNum;
   }
   close(INFILE);
   return $lineNum;
}

# Processes the file line-by-line, removing duplicate <?xml> and 
# <!DOCTYPE> tags and extracting the fields listed above. It has to be 
# done line-by-line (hence the use of XML::Twig rather than XML:Simple)
# rather than loading the entire .xml file into memory because the files 
# are far too big to fit.
sub processFile {
   my $buffer = "", my $firstItem = 1, my $currentLine = 1;

   open(INFILE, "data/".$_[0].".xml") or die "Can't open ".$_[0].": $!";
   unlink("details/".$_[0].".xml");
   unlink("citations/".$_[0].".xml");
   open(my $detailsFile, ">>details/".$_[0].".xml") or die "Can't output ".$_[0].": $!";
   open(my $citationsFile, ">>citations/".$_[0].".xml") or die "Can't output ".$_[0].": $!";
   
   # Prints the root node to the files for XML::Simple in generateSQL()
   #print $detailsFile "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<PATDOC>";
   #print $citationsFile "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<PATDOC>\n";
   
   # For each line, build up a buffer (excluding the <?xml> and 
   # <!DOCTYPE> tags). When the next <us-patent-grant> item is reached
   # (a.k.a. when the next <?xml> tag after the initial one is reached),
   # run the buffer through the details and citations twigs and print
   # the results to the relevant files. Then clear the buffer for the next
   # <us-patent-grant>
   foreach(<INFILE>) {
      print "Processing line ".($currentLine++)."/".$_[1]."...\n";
      
      #if ($_ !~ /^\<\?xml/ && $firstItem == 0) {
         #if ($_ !~ /^\<\!DOCTYPE/) {
         #}
      #} elsif ($firstItem == 1) {
       #  $firstItem = 0;
      #} else {
      if ($_ =~ /^\<\?xml/ && $firstItem == 0) {	
	 #print "\n----\n".$buffer."\n----\n"; 	 
	 $patentTwig->parse($buffer);
	 $patentTwig->print($detailsFile);
         $citationTwig->parse($buffer);
         $citationTwig->print($citationsFile);
       
         $buffer = "";
      } elsif ($_ !~ /^\<\!/ && $_ !~ /^\]\>/) { 
	 if ($firstItem == 0) {
  		$string = $_;
                $string =~ s/\&[a-zA-Z0-9]*;/zonk/g;
	 	$buffer = $buffer.$string;
		
	 } else {
	    
   		print $detailsFile "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<patents>";
   		print $citationsFile "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<patents>\n";
	    	$firstItem = 0;
	 } 
      }
   }
   
   print $detailsFile "</patents>";
   print $citationsFile "</patents>";
   
   close($detailsFile);
   close($citationsFile);
   close(INFILE);
}

# Generates an SQL dump of the database formed from analysing the .xml
# files.
sub generateSQL {
   my $xml = new XML::Simple (KeyAttr=>[]);

   my $details = $xml->XMLin("details/".$_[0].".xml");
   
   unlink("sql/".$_[0].".sql");
   open(my $sqlFile, ">>sql/".$_[0].".sql") or die "Can't output SQL ".$_[0].": $!";
   
   print $sqlFile "CREATE TABLE IF NOT EXISTS `patent`\n(\n\t`pid` INT NOT NULL AUTO_INCREMENT,\n\t`pubNum` VARCHAR(32),\n\t`pubDate` DATETIME,\n\t`appNum` VARCHAR(32),\n\t`appDate` DATETIME,\n\tPRIMARY KEY(`pid`)\n);\n\nCREATE TABLE IF NOT EXISTS `patent_cite`\n(\n\t`citing_id` VARCHAR(32) NOT NULL,\n\t`cited_id` VARCHAR(32) NOT NULL,\n\tPRIMARY KEY (`citing_id`, `cited_id`)\n);\n\n";
   print $sqlFile "INSERT INTO `patent` (`pubNum`, `pubDate`, `appNum`, `appDate`) VALUES";
   foreach my $e (@{$details->{'PATDOC'}}) {
      print $sqlFile "\n\t('".$e->{'pubnum'}."', '".$e->{'pubdate'}."', '".$e->{'appnum'}."', '".$e->{'appdate'}."'),";
   }
   print $sqlFile "\n\t('0', '0', '0', '0');\n\n-- This line and the above (0,0,0,0) tuple are needed due to the nature\n-- of the loop that builds the INSERT query, and the resultant SQL file\n-- being too long to edit from the end easily.\nDELETE FROM `patent` WHERE `pid` = '0';";
   
   my $citations = $xml->XMLin("citations/".$_[0].".xml");
   
   print $sqlFile "\n\nINSERT INTO `patent_cite` (`citing_id`, `cited_id`) VALUES";
   foreach my $f (@{$citations->{'PATDOC'}}) {
      my $pubNum = $f->{'pubnum'};
      foreach (@{$f->{'citing'}}) {
         print $sqlFile "\n\t('".$pubNum."', '".$_."'),";
      }
   }
   print $sqlFile "\n\t('0', '0', '0', '0');\n\n-- This line and the above (0,0,0,0) tuple are needed due to the nature\n-- of the loop that builds the INSERT query, and the resultant SQL file\n-- being too long to edit from the end easily.\nDELETE FROM `patent_cite` WHERE `citing_id` = '0';";
   
   close($sqlFile);
}
