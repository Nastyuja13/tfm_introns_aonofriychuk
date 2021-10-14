import config
import sqlite3
import random

# exon lens indiv in a gene

def exon_len(exons):
	exon_len = []

	for exon_key in exons:
		exon = exons[exon_key]
		exlen = abs(exon['end']- exon['start'])
		exon_len.append(exlen)

	return exon_len

# exon lengths total in a gene

def total_exon_len(exon_len):

	total_exon_len = sum(exon_len)

	return total_exon_len

# same for introns
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
		gene_len = abs(gene['end'] - gene['start'])
		total_genes.append(gene_len)

	total_len = sum(total_genes)

	avg_gene_len = total_len / len(genes.keys())

	return avg_gene_len

# genes/ genome
# no genes of each species
# UTR size
# median transcripts/ genome

# Check if same strand for all exons

def _det_strand(exons):

	i = 0

	for exon in exons:
		if i == 0:
			prev_strand = exon[strand]
			i = 1
			continue
		else:
			pass

		strand = exon[strand]
		if strand == prev_strand:
			prev_strand = strand
			continue
		else:
			print('ERROR DIFFERENT STRANDS IN EXONS')
			return
			
	return strand




#db_connect = sqlite3.connect(config.NEW_DB_DIR / 'Apis_mellifera.Amel_HAv3.1.51.sql') 
db_connect = sqlite3.connect(config.NEW_DB_DIR / 'Drosophila_melanogaster.BDGP6.32.51.sql') 
cur = db_connect.cursor()

cur.execute('SELECT gene_id, start, end FROM genes')

genes_lens = {gene[0]: {'start': gene[1], 'end': gene[2]} for gene in cur.fetchall()}

cur.execute('SELECT gene_id FROM genes')

genes = [gene[0] for gene in cur.fetchall()]

print('Number of genes:' + str(len(genes)))
print('Avg gene len:' + str(avg_gene_len(genes_lens)))

cur.execute('SELECT trans_id FROM transcripts')
ts = [t[0] for t in cur.fetchall()]

print('Number of transcripts:' + str(len(ts)))

print(avg_trans_per_gene(ts, genes))

cur.execute('SELECT exon_id FROM exons')
ex = [e[0] for e in cur.fetchall()]

print('Number of exons:' + str(len(ex)))

print(avg_exon_per_trans(ex, ts))
print(avg_exon_per_gene(ex, genes))

i = 0

for gene in genes:

	i = i + 1

	print('### Gene:' + gene)

	cur.execute('SELECT trans_id FROM transcripts WHERE gene_id = ?', (gene,))
	transcripts = [trans[0] for trans in cur.fetchall()]
	#print(transcripts)

	transcript_id = random.choice(transcripts)
	print('# Transcript:' + transcript_id)

	cur.execute('SELECT exon_id, start, end, strand FROM exons WHERE transcript_id = ?', (transcript_id,))
	exons = {exon[0]: {'start': exon[1], 'end': exon[2], 'strand': exon[3]} for exon in cur.fetchall()}

	print(exons)

	print(exon_len(exons))
	print(total_exon_len(exon_len(exons)))




    #exon_positions = res['exon_positions']

    #exon_positions = sorted(exon_positions, key=lambda x: x[0])
    #intron_len = 0
    #for exon_a, exon_b in zip(exon_positions[:-1], exon_positions[1:]):
        #intron_len += abs(exon_b[0] - exon_a[1])

	if i == 3:
		db_connect.close()
		break
