import config
import sqlite3
import random
import plot
import numpy
import seaborn as sns
import pandas as pd

# exon lens indiv in a gene

def exon_len(exons):
	exon_len = []

	for exon_key in exons:
		exon = exons[exon_key]
		exlen = abs(exon['end']- exon['start']) + 1
		exon_len.append(exlen)

	return exon_len

# exon lengths total in a gene

def total_exon_len(exon_len):

	total_exon_len = sum(exon_len)

	return total_exon_len

# introns lens in a gene

def intron_len(exons):

	intron_len = []

	strand = _det_strand(exons)

	if strand == False:
		print('ERROR: NO STRAND SPECIFIED')
		pass

	A = -1
	B = -1

	first_time = True

	for exon in exons:

		exon = exons[exon]

		if first_time == True:
			A = exon['end']
			first_time = False
		else:
			B = exon['start']
			int_len = B - A - 1
			intron_len.append(int_len)
			A = exon['end']

	return intron_len

# intron lengths total in a gene

def total_intron_len(intron_len):

	total_intron_len = sum(intron_len)

	return total_intron_len

# avg transcripts per gene

def avg_trans_per_gene(trans, genes):

	avg = len(trans)/len(genes)

	return avg


# avg exons per transcript

def avg_exon_per_trans(exons, trans):

	avg = len(exons)/len(trans)

	return avg

# avg exon per gene

def avg_exon_per_gene(exons, genes):

	avg = len(exons)/len(genes)

	return avg

# avg gene length
def avg_gene_len(genes):

	total_genes = []

	for gene_key in genes:
		gene = genes[gene_key]
		gene_len = abs(gene['end'] - gene['start']) + 1
		total_genes.append(gene_len)

	total_len = sum(total_genes)

	avg_gene_len = round(total_len / len(genes.keys()), 3)

	return avg_gene_len

# genes/ genome
# no genes of each species
# UTR size
# median transcripts/ genome

# Check if same strand for all exons

def _det_strand(exons):

	i = 0

	for exon in exons:

		exon = exons[exon]

		if i == 0:
			prev_strand = exon['strand']
			i = 1
			continue
		else:
			pass

		strand = exon['strand']
		if strand == prev_strand:
			prev_strand = strand
			continue
		else:
			print('ERROR: DIFFERENT STRANDS IN EXONS')
			return
			
	return strand