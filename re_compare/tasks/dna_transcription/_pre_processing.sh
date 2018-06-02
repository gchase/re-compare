#!/bin/bash

# remove junk from text
#TODO change to cat all fasta urls and then process them
cat $1/chr*.fsa | awk 'NR % 2 == 0' | tr -d '\n' > temp_file
mv temp_file $1/dna

#partition to sizes
head -c $((10**3)) $1/dna > $1/_10e3
head -c $((10**5)) $1/dna > $1/_10e5
head -c $((10**7)) $1/dna > $1/_10e7

#cleanup
rm $1/dna $1/chr*.fsa
