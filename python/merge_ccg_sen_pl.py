#!/usr/bin/env python3
# -*- coding: utf8 -*-

# usage
# python/merge_ccg_sen_pl.py --output merged_file_ccg.pl --ccg-pl file1_ccg.pl file2_ccg.pl
# python/merge_ccg_sen_pl.py --output merged_file_sen.pl --sen-pl file1_sen.pl file2_sen.pl

import argparse
import sys
import re

#################################
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Merge ccg_pl or sen_pl data. IMPORTANT: merged ccg_pl and sen_pl files are compatible if the order of merged files are the same")
    parser.add_argument(
    '--ccg-pl', nargs='+', metavar='ccg.pl FILES',
        help='Files formatted as ccg.pl')
    parser.add_argument(
    '--sen-pl', nargs='+', metavar='sen.pl FILES',
        help='Files formatted as sen.pl')
    parser.add_argument(
    '--output', metavar='FILE PATH',
        help='path to the file where merge data will be written')
    parser.add_argument(
    '-v', '--verbose', dest='v', action='count',
        help='verbosity level of reporting')
    args = parser.parse_args()
    return args

#################################
def read_ccg_pl(ccg_pl, add=0):
    '''Read ccg_pl file content. It is expected that comments (if any) are
       at the beginning, followed by operator declarations (if any), and
       the rest are a list of ccg terms
    '''
    with open(ccg_pl) as F:
        content = F.read()
    content = re.split('\s*\n+\s*\n+\s*', content)
    comments, preambule, ccgs = '', '', []
    for c in content:
        if c.startswith('%'):
            comments = c
        elif c.startswith(':-'):
            preambule = c
        elif c.startswith('ccg('):
            i = int(re.match('ccg\((\d+),', c).group(1)) + add
            ccgs.append(re.sub('ccg\(\d+,', 'ccg({},'.format(i), c))
    return comments, preambule, ccgs, i


#################################
def read_sen_pl(sen_pl, add=0):
    '''Read sen_pl file content. It is expected that comments (if any) are
       at the beginning, followed by operator declarations (if any), and
       the rest are a list of ccg terms
    '''
    with open(sen_pl) as F:
        content = F.read()
    content = re.split('\s*\n+\s*', content)
    sens = []
    for c in content:
        if c.startswith('sen_id('):
            i = int(re.match('sen_id\((\d+),', c).group(1)) + add
            sens.append(re.sub('sen_id\(\d+,', 'sen_id({},'.format(i), c))
    return sens, i


#################################
if __name__ == '__main__':
    args = parse_arguments()
    # writing ccgs in prolog file
    if args.ccg_pl is not None:
        add, comments, preambule = 0, [], ''
        all_ccgs = []
        for ccg_pl in args.ccg_pl:
            com, pre, ccgs, add = read_ccg_pl(ccg_pl, add=add)
            if com:
                comments.append(com)
            if pre:
                preambule = pre
            all_ccgs += ccgs
        with open(args.output, 'w') as F:
            F.write('% Generated by the command:\n% {}\n\n'.format(' '.join(sys.argv)))
            F.write('\n'.join(comments) + '\n\n')
            F.write(preambule + '\n\n')
            for ccg in all_ccgs:
                F.write(ccg + '\n\n')
    # writing sens in prolog file
    elif args.sen_pl is not None:
        add = 0
        all_sens = []
        for sen_pl in args.sen_pl:
            sens, add = read_sen_pl(sen_pl, add=add)
            all_sens += sens
        with open(args.output, 'w') as F:
            F.write('% Generated by the command:\n% {}\n\n'.format(' '.join(sys.argv)))
            pid = None
            for sen in all_sens:
                id = re.match('sen_id\(\d+,\s*(\d+),', sen).group(1)
                if pid != id:
                    pid = id
                    F.write("% problem id = {}\n".format(pid))
                F.write(sen + '\n')
    else:
        raise ValueError('Insufficient arguments passed')
