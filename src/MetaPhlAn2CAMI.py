# This file will take a MetaPhlAn profile and use the taxonomy_taxid to convert to the CAMI format
# Note that this is a lossy format conversion as MetaPhlAn includes stuff like:
# XYZ_unclassified which is really hard to figure out how to handle
import os

metaphlan_file = '/home/dkoslicki/Dropbox/Repositories/CAMIMetaPhlAn/test.tsv'
taxonomy_file = '/home/dkoslicki/Dropbox/Repositories/CAMIMetaPhlAn/taxonomy_reduced_taxID_27032017.txt'
output_file = '/home/dkoslicki/Dropbox/Repositories/CAMIMetaPhlAn/test.profile'

# Read in the MetaPhlAn profile
input_taxonomy = []
input_abundance = []
fid = open(metaphlan_file, 'r')
for line in fid:
    line = line.strip().split()
    tax_path = line[0]
    abundance = float(line[1])
    input_taxonomy.append(tax_path.split('|')[-1])
    input_abundance.append(abundance)

fid.close()

# Read in the reference taxonomy
reference_taxonomy = dict()
i = 0
fid = open(taxonomy_file, 'r')
for line in fid:
    line = line.strip().split()
    entry = dict()
    #i += 1
    #if i > 1000:
    #    break
    #name = '_'.join(line[0].split('_')[1:])
    tax_id = line[1]
    full_tax_path = line[2]
    name = full_tax_path.split('|')[-1].split('_')
    name.pop(2)
    name = '_'.join(name)
    tax_id_path = '|'.join([item.split('_')[2] for item in full_tax_path.split('|')])
    tax_path_sn = '|'.join(['_'.join(item.split('_')[3:]) for item in full_tax_path.split('|')])
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
