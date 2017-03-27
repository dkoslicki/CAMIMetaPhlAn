# CAMIMetaPhlAn

## How to use
First, create the taxonomy using the modified repophlan script:

```
#~/bin/sh
mkdir -p out
t=`date "+%d%m%Y"`/local/cluster/bin/python generate_taxonomy_taxid.py --output out/taxonomy_taxID_${t}.txt --output_red out/taxonomy_reduced_taxID_${t}.txt --pickle out/taxonomy_taxID_${t}.pkl | tee out/generate_taxonomy_tax_ID${t}.txt
```
