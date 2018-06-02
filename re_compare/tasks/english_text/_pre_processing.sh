#!/bin/bash

# get abstract texts
# went here: https://aminer.org/citation
# downloaded the entry: DBLP-Citation-network V3:  1,632,442 papers and >2,327,450 citation relationships (2010-10-22).

#1. untar and get filename: DBLPOnlyCitationOct19.txt
tar -xvzf $1/DBLP-citation-network-Oct-19.tar.gz

#2. ran `grep "\#\!" > abstracts.txt`
grep "\#\!" $1/DBLPOnlyCitationOct19.txt > $1/abstracts.txt

#3. got unique lines
sort $1/abstracts.txt | uniq  > $1/abstract_uniq.txt

#4. partition to sizes
head -c $((10**3)) $1/abstract_uniq.txt > $1/_10e3
head -c $((10**5)) $1/abstract_uniq.txt > $1/_10e5
head -c $((10**7)) $1/abstract_uniq.txt > $1/_10e7

#5. cleanup
rm $1/DBLP-citation-network-Oct-19.tar.gz $1/DBLPOnlyCitationOct19.txt $1/abstracts.txt
