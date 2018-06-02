#!/bin/env python

#format taken from
#https://en.wikipedia.org/wiki/FASTA_format

fasta_to_regex_dict={
        'A':'A',
        'C':'C',
        'G':'G',
        'T':'T',
        'U':'U',
        'R':'[AG]',
        'Y':'[CTU]',
        'K':'[GTU]',
        'M':'[AC]',
        'S':'[GC]',
        'W':'[ATU]',
        'B':'[CGTU]',
        'D':'[AGTU]',
        'H':'[ACTU]',
        'V':'[ACG]',
        'N':'.',
        '-':'.*'
        }



def fasta_to_regex(fasta_string):
    global fasta_to_regex_dict
    transformed=[fasta_to_regex_dict[i] for i in fasta_string]

    regex="".join(transformed)
    return regex





def fasta_file_to_Regex_file(from_file, to_file):
    with  open(from_file,"r") as inptr:
        inlines=inptr.readlines()
        inlines=[ i[:-1] for i in inlines if i[-1]=="\n"]
    with   open(to_file,"w") as outptr:
        outlines=[fasta_to_regex(i)+"\n" for i in inlines ]
        outptr.writelines(outlines)

    return

def main():
    import sys
    fromfile=sys.argv[1]
    tofile=sys.argv[2]
    fasta_file_to_Regex_file(fromfile,tofile)



if  __name__ == '__main__' :
    main()

