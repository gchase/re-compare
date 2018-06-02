#!/bin/python

import requests


def main():
    factors_list_page = requests.get('http://rulai.cshl.edu/cgi-bin/SCPD/getfactorlist')
    factors_list = []
    for line in factors_list_page.text.split('\n'):
        if 'getfactor?' in line:
            factor = line[line.find('getfactor?') + len('getfactor?'): line.find('">')]
            factors_list.append(factor)

    extracted_factor_patterns = []
    for factor in factors_list:
        factor_page = requests.post('http://rulai.cshl.edu/cgi-bin/SCPD/getfactor?%s' % factor, {'action': 'Get consensus'})
        extracted_factor = factor_page.text[factor_page.text.find('pre>\t\t') + len('pre>\t\t'):-1].replace('\t', '')
        if 'No consensus available' != extracted_factor:
            for factor_pattern in extracted_factor.split(' or '):
                print(factor_pattern)
                extracted_factor_patterns.append(factor_pattern)

    with open('transcriptional_factors_patterns', 'w') as output_file:
        for patern in extracted_factor_patterns:
            output_file.write('%s\n' % patern)


if '__main__' == __name__:
    main()
