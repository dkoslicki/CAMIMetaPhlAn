# This file will take a MetaPhlAn profile and use the taxonomy_taxid to convert to the CAMI format
# Note that this is a lossy format conversion as MetaPhlAn includes stuff like:
# XYZ_unclassified which is really hard to figure out how to handle
import os
import argparse
import sys

__author__ = 'David Koslicki (dmkoslicki@gmail.com, david.koslicki@math.oregonstate.edu)'
__version__ = '1.0.0'
__date__ = '27 Mar 2017'

#metaphlan_file = '/home/dkoslicki/Dropbox/Repositories/CAMIMetaPhlAn/test.tsv'
#taxonomy_file = '/home/dkoslicki/Dropbox/Repositories/CAMIMetaPhlAn/taxonomy_reduced_taxID_27032017.txt'
#output_file = '/home/dkoslicki/Dropbox/Repositories/CAMIMetaPhlAn/test.profile'

def read_params(args):
    parser = argparse.ArgumentParser(description='')
    arg = parser.add_argument
    arg('--input', metavar='metaphlan_file', type=str, required=True,
         default=None,
         help="Input Metaphlan.tsv file")
    arg('--output', metavar='output_file', required=True, default=None, type=str,
         help="Output file (you should have this end in .profile)")
    arg('--taxonomy', metavar='taxonomy_file', required=True, default=None, type=str,
         help="Taxonomy file from generate_taxonomy_taxid.py (after removing norank and noname, see README)")
    return vars(parser.parse_args())

def convert(metaphlan_file, output_file, taxonomy_file):
    # Read in the MetaPhlAn profile
    input_taxonomy = []
    input_abundance = []
    fid = open(metaphlan_file, 'r')
    for line in fid:
        if line[0] != '#':
            line = line.strip().split()
            tax_path = line[0]  # MetaPhlAn2 only gives the names, so use these (they have <rank>__ prepended)
            abundance = float(line[1])
            tax_path_split = tax_path.split('|')
            # Don't include terminating repeat tax_paths
            if len(tax_path_split) > 1:
                if '_'.join(tax_path_split[-1].split('_')[2:]) == '_'.join(tax_path_split[-2].split('_')[2:]):
                    continue
                else:
                    input_taxonomy.append(tax_path_split[-1])  # Add the terminal dude
                    input_abundance.append(abundance)  # Also include the associated abundance
            else:
                input_taxonomy.append(tax_path_split[-1])
                input_abundance.append(abundance)

    fid.close()

    # Read in the reference taxonomy
    reference_taxonomy = dict()
    i = 0
    fid = open(taxonomy_file, 'r')
    for line in fid:
        line = line.strip().split()
        entry = dict()
        tax_id = line[1]
        full_tax_path = line[2]
        name = full_tax_path.split('|')[-1].split('_')  # get full name
        name.pop(2)  # drop off the taxID identifier
        name = '_'.join(name)  # re-join it up
        #tax_id_path = '|'.join([item.split('_')[2] for item in full_tax_path.split('|')])  # get the taxIDs in order
        # tax_path_sn = '|'.join(['_'.join(item.split('_')[3:]) for item in full_tax_path.split('|')])  # get the names in order
        tax_id_path_list = [item.split('_')[2] for item in full_tax_path.split('|')]  # get the taxIDs in order
        tax_path_sn_list = ['_'.join(item.split('_')[3:]) for item in full_tax_path.split('|')]
        seen_list = set()
        for i in range(len(tax_id_path_list)):
            if tax_id_path_list[i] in seen_list:
                tax_id_path_list[i] = ''
                tax_path_sn_list[i] = ''
            else:
                seen_list.add(tax_id_path_list[i])
        tax_id_path = '|'.join(tax_id_path_list)
        tax_path_sn = '|'.join(tax_path_sn_list)
        entry['tax_id'] = tax_id
        entry['tax_id_path'] = tax_id_path
        entry['tax_path_sn'] = tax_path_sn
        reference_taxonomy[name] = entry

    fid.close()

    letter_to_rank = dict()
    letter_to_rank['k'] = 'superkingdom'
    letter_to_rank['p'] = 'phylum'
    letter_to_rank['c'] = 'class'
    letter_to_rank['o'] = 'order'
    letter_to_rank['f'] = 'family'
    letter_to_rank['g'] = 'genus'
    letter_to_rank['s'] = 'species'
    letter_to_rank['t'] = 'strain'

    # Put in CAMI format
    fid = open(output_file, 'w')
    fid.write('# Taxonomic profile for the file: %s\n' % metaphlan_file)
    fid.write('@Version:0.9.1\n')
    fid.write('@SampleID:%s\n' % os.path.basename(metaphlan_file))
    fid.write('@Ranks: superkingdom|phylum|class|order|family|genus|species|strain\n')
    fid.write('@@TAXID \t RANK \t TAXPATH \t TAXPATHSN \t PERCENTAGE\n')
    for line_num in xrange(len(input_taxonomy)):
        name = input_taxonomy[line_num]
        if name in reference_taxonomy:
            # Need to carefully get rid of repeated taxids
            entry = reference_taxonomy[name]
            tax_id = entry['tax_id']
            rank = letter_to_rank[name.split('_')[0]]
            tax_id_path = entry['tax_id_path']
            tax_path_sn = entry['tax_path_sn']
            abundance = input_abundance[line_num]
            fid.write("%s \t %s \t %s \t %s \t %f\n" % (tax_id, rank, tax_id_path, tax_path_sn, abundance))
        else:
            print('Warning: taxa %s not found in reference taxonomy' % name)
            # Unfortunately there are spelling discrepancies. Eg: o__Enterobacterales vs o__Enterobacteriales

    fid.close()

if __name__ == '__main__':
    par = read_params(sys.argv)
    convert(par['input'], par['output'], par['taxonomy'])
