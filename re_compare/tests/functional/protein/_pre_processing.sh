#!/bin/bash

# remove junk from text
cat $1/pdb_seqres.txt | awk 'NR % 2 == 0' | tr -d '\n' > temp_file
mv temp_file $1/pdb_seqres.txt

#partition to sizes
head -c $((10**3)) $1/pdb_seqres.txt > $1/_10e3
head -c $((10**5)) $1/pdb_seqres.txt > $1/_10e5
head -c $((10**7)) $1/pdb_seqres.txt > $1/_10e7

#cleanup
rm $1/pdb_seqres.txt
