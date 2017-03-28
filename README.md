# CAMIMetaPhlAn

## How to use
First, create the taxonomy using the modified repophlan script:

```
#~/bin/sh
mkdir -p out
t=`date "+%d%m%Y"`/local/cluster/bin/python generate_taxonomy_taxid.py --output out/taxonomy_taxID_${t}.txt --output_red out/taxonomy_reduced_taxID_${t}.txt --pickle out/taxonomy_taxID_${t}.pkl | tee out/generate_taxonomy_tax_ID${t}.txt
sed -i 's/norank__1_root|//g' out/taxonomy_reduced_taxID_${t}.txt
sed -i 's/_noname//g' out/taxonomy_reduced_taxID_${t}.txt
```
Then do the following to get from metaphlan to cami output:
```
#Run MetaPhlAn2
zcat ${input} | ${metaphlanloc}/./metaphlan2.py --input_type multifasta --bowtie2db ${metaphlanloc}/db_v20/mpa_v20_m200 --bowtie2out ${outfolder}/`basename ${input}`.bowtie2out.txt -t rel_ab --nproc 48 > ${outfolder}/`basename ${input}.metaphlan.tsv`

# Convert to CAMI output
sed -i 's/_noname//g' ${outfolder}/`basename ${input}.metaphlan.tsv`
/local/cluster/bin/python MetaPhlAn2CAMI.py --input ${outfolder}/`basename ${input}.metaphlan.tsv` --output ${outfolder}/`basename ${input}.metaphlan.profile` --taxonomy taxonomy_reduced_taxID_${t}.txt
```
