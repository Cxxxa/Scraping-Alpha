#!/usr/bin/perl

use 5.010;
use strict;
use warnings;
use XML::Parser;
use XML::SimpleObject;

my $file = 'ipg150106.xml';

my $parser = XML::Parser->new(ErrorContext => 2, Style => "Tree");
my $xso = XML::SimpleObject->new( $parser->parsefile($file) );

foreach my $patent ($xso->child('us-patent-grant')) {
    print $patent->child('invention-title')->{VALUE};
    print "\n";
}