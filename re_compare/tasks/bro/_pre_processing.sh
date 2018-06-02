#!/bin/bash

gunzip $1/outside.tcpdump.gz

#convert from pcap to text
tshark -V -r  $1/outside.tcpdump > $1/dump.txt

#partition to sizes
head -c $((10**3)) $1/dump.txt > $1/_10e3
head -c $((10**5)) $1/dump.txt > $1/_10e5
head -c $((10**7)) $1/dump.txt > $1/_10e7

#cleanup
rm $1/dump.txt
