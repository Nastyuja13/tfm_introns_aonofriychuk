import config
import sqlite3
import random
import requests
import re
import plotly.io as pli
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy
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


# Obtain golden path length for a genome
def get_golden_path_len(gff_name, species_type):
	#http://metazoa.ensembl.org/Apis_mellifera/Info/Annotation/
	#http://www.ensembl.org/Felis_catus/Info/Index
	#http://fungi.ensembl.org/Saccharomyces_cerevisiae/Info/Annotation/#assembly
	#http://protists.ensembl.org/Plasmodium_falciparum/Info/Annotation/#assembly
	#http://plants.ensembl.org/Arabidopsis_thaliana/Info/Annotation/#assembly
	spc = gff_name.split('.')[0]
	
	if species_type == 'plant':
		html_path = "http://{a}s.ensembl.org/{b}/Info/Annotation/".format(a=species_type, b=spc)
	elif species_type != 'main':
		html_path = "http://{a}.ensembl.org/{b}/Info/Annotation/".format(a=species_type, b=spc)
	else:
		html_path = "http://www.ensembl.org/{b}/Info/Annotation/".format(b=spc)

	html = requests.get(html_path).text

	match = re.search('<b>Golden Path Length</b></td>[^>]+>(?P<genome_size>[^<]+)</td>', html, re.I)
	#<b>Golden Path Length</b></td><td style="width:70%;text-align:left">100,286,401</td>

	if not match:
		genome_length = -1
		#raise RuntimeError('No golden path found')
	else:
		genome_length = int(match['genome_size'].replace(',', ''))

	return genome_length


# Getting genomic stats for each species database
def get_gene_stats(gff_name, species, genome_length, gene_type = None):

	sql = gff_name + '.sql'

	db_connect = sqlite3.connect(config.NEW_DB_DIR / sql) 
	cur = db_connect.cursor()

	queries = {'query_gene_count': 'SELECT count(gene_id) FROM genes',
			   'query_avg_gene_len': 'SELECT avg(end-start+1) FROM genes',
			   'query_trans_count': 'SELECT count(trans_id) FROM transcripts',
			   'query_exon_count': 'SELECT count(exon_id) FROM exons',
			   'query_avg_exon_len': 'SELECT avg(end-start+1) FROM exons',
			   'query_gene_ids': 'SELECT gene_id FROM genes'
			   }

	if gene_type == None:
		pass
	else:
		condition = 'biotype LIKE "' + gene_type + '"'

		queries['query_gene_count'] = queries['query_gene_count'] + ' WHERE '
		queries['query_avg_gene_len'] = queries['query_avg_gene_len'] + ' WHERE '
		queries['query_gene_ids'] = queries['query_gene_ids'] + ' WHERE '

		queries['query_trans_count'] = 'SELECT count(t.trans_id) FROM transcripts t JOIN genes g ON (t.gene_id = g.gene_id) WHERE g.'
		queries['query_exon_count'] = 'SELECT count(e.exon_id) FROM exons e JOIN transcripts t ON (t.trans_id = e.transcript_id) JOIN genes g ON (t.gene_id = g.gene_id) WHERE g.'
		queries['query_avg_exon_len'] = 'SELECT avg(e.end-e.start+1) FROM exons e JOIN transcripts t ON (t.trans_id = e.transcript_id) JOIN genes g ON (t.gene_id = g.gene_id) WHERE g.'

		for query in queries.keys():
			queries[query] = queries[query] + condition

	# Select genes
	## Calculate general genomic stats
	cur.execute(queries['query_gene_count'])
	gene_num = cur.fetchall()[0][0]
	cur.execute(queries['query_avg_gene_len'])
	avg_gene_len = round(cur.fetchall()[0][0], 3)

	cur.execute(queries['query_trans_count'])
	trans_num = cur.fetchall()[0][0]
	avg_trans_per_gene = round(trans_num/gene_num, 3)

	cur.execute(queries['query_exon_count'])
	exon_num = cur.fetchall()[0][0]
	avg_exon_per_trans = round(exon_num/trans_num, 3)
	avg_exon_per_gene = round(exon_num/gene_num, 3)
	cur.execute(queries['query_avg_exon_len'])
	avg_exon_len = round(cur.fetchall()[0][0], 3)

	# Gene density in genes per megabase
	gene_dens = round((gene_num/genome_length) * 1000000, 4)

	## Calculate stats related to introns

	cur.execute(queries['query_gene_ids'])

	genes = [gene[0] for gene in cur.fetchall()] # List of all gene IDs to process

	genes_with_introns = 0
	intron_gene_ids = []

	all_introns = [] # Lengths of all the introns in the selected transcripts, concatenated
	all_intron_num = [] # Number of introns in each selected transcript, concatenated
	all_tot_introns = [] # Total intron length of every selected gene
	all_first_introns = [] # First intron length of every selected gene

	for gene in genes:

		cur.execute('SELECT trans_id FROM transcripts WHERE gene_id = ?', (gene,))
		transcripts = [trans[0] for trans in cur.fetchall()]

		transcript_id = random.choice(transcripts) # Selection of a random transcript

		cur.execute('SELECT exon_id, start, end, strand FROM exons WHERE transcript_id = ?', (transcript_id,))
		exons = {exon[0]: {'start': exon[1], 'end': exon[2], 'strand': exon[3]} for exon in cur.fetchall()}

		ex_len = exon_len(exons) # List with length of all exons of a transcript (individually)
		ex_str = list(exons.values())[0]['strand'] # strand of the gene
		tot_ex_len = total_exon_len(ex_len) # Sum of the lengths of all the exons of a transcript
		if len(ex_len) > 1: # If more that 1 exon, there should be an intron

			int_len = intron_len(exons) # Lengths of all introns of a transcript (individually)

			# Check if there a 0 bp introns (two exons together)
			while 0 in int_len:
				int_len.remove(0)

			if len(int_len) == 0:
				continue # Continue if no intons
			else:
				pass

			genes_with_introns = genes_with_introns + 1 # Count a gene with introns
			intron_gene_ids.append(gene)

			tot_int_len = total_intron_len(int_len) # Total intron length (sum) of a transcript

			all_introns = all_introns + int_len # Concatenate all intron lengths
			all_tot_introns.append(tot_int_len) # Concatenate total intron length
			if ex_str == '+':
				all_first_introns.append(int_len[0]) # concatenate first intron length
			elif ex_str == '-':
				all_first_introns.append(int_len[-1]) # concatenate first intron length if negative strand
			all_intron_num.append(len(int_len)) # Concatenate intron number of a trancript
		else:
			pass

	avg_intron_num_per_gene = round(sum(all_intron_num)/gene_num, 3)
	avg_intron_num_per_gene_with_introns = round(sum(all_intron_num)/genes_with_introns, 3)
	avg_intron_len = round(sum(all_introns)/len(all_introns), 3)
	cur.execute('SELECT avg(end-start+1) FROM genes WHERE gene_id IN (%s)' % ','.join('?'*len(intron_gene_ids)), intron_gene_ids)
	avg_intron_gene_len = round(cur.fetchall()[0][0], 3)
	avg_first_intron_len = round(sum(all_first_introns)/len(all_first_introns), 3)
	avg_total_intron_len = round(sum(all_tot_introns)/len(all_tot_introns), 3)

	intron_gene_dens = round((genes_with_introns/genome_length) * 1000000, 4)

	cur.execute('SELECT avg(e.end-e.start+1) FROM exons e JOIN transcripts t ON (t.trans_id = e.transcript_id) JOIN genes g ON (t.gene_id = g.gene_id) WHERE g.gene_id IN (%s)' % ','.join('?'*len(intron_gene_ids)), intron_gene_ids)
	avg_exon_len_in_int_genes = round(cur.fetchall()[0][0], 3)

	gene_info = {'gff_name': gff_name,
				 'gene_num': gene_num,
				 'genes_with_introns_num': genes_with_introns,
				 'trans_num': trans_num,
				 'exon_num': exon_num,
				 'gene_dens': gene_dens,
				 'intron_gene_dens': intron_gene_dens,
				 'avg_gene_len': avg_gene_len,
				 'avg_intron_gene_len': avg_intron_gene_len,
				 'avg_exon_len': avg_exon_len,
				 'avg_exon_len_in_int_genes': avg_exon_len_in_int_genes,
				 'avg_trans_per_gene': avg_trans_per_gene,
				 'avg_exon_per_trans': avg_exon_per_trans,
				 'avg_exon_per_gene': avg_exon_per_gene,
				 'avg_intron_num_per_gene': avg_intron_num_per_gene,
				 'avg_intron_num_per_gene_with_introns': avg_intron_num_per_gene_with_introns,
				 'avg_intron_len': avg_intron_len,
				 'avg_first_intron_len': avg_first_intron_len,
				 'avg_total_intron_len': avg_total_intron_len
				 }


	# Construct graph objects for the species

	## first introns length

	box_1 = go.Box(y=all_first_introns, name=species, boxpoints='all', jitter=0.5, whiskerwidth=0.4,
				  marker_size=2, line_width=1.25, boxmean=True)
	box_1_json = pli.to_json(box_1)

	try:
		log_introns = numpy.around(numpy.log10(all_first_introns), 4)

		dist_1 = ff.create_distplot([log_introns], 
			group_labels = [species], bin_size=0.05)
		dist_1_json = pli.to_json(dist_1)
	except numpy.linalg.LinAlgError:
		dist_1_json = ''

	## all introns length

	box_all = go.Box(y=all_introns, name=species, boxpoints='all', jitter=0.5, whiskerwidth=0.4,
				  marker_size=2, line_width=1.25, boxmean=True)
	box_all_json = pli.to_json(box_all)

	try:
		log_introns = numpy.around(numpy.log10(all_introns), 4)

		dist_all = ff.create_distplot([log_introns], 
			group_labels = [species], bin_size=0.05)
		dist_all_json = pli.to_json(dist_all)
	except numpy.linalg.LinAlgError:
		dist_all_json = ''

	## total intron length

	box_tot = go.Box(y=all_tot_introns, name=species, boxpoints='all', jitter=0.5, whiskerwidth=0.4,
				  marker_size=2, line_width=1.25, boxmean=True)
	box_tot_json = pli.to_json(box_tot)

	try:
		log_introns = numpy.around(numpy.log10(all_tot_introns), 4)

		dist_tot = ff.create_distplot([log_introns], 
			group_labels = [species], bin_size=0.05)
		dist_tot_json = pli.to_json(dist_tot)
	except numpy.linalg.LinAlgError:
		dist_tot_json = ''

	## intron number in a gene

	box_num = go.Box(y=all_intron_num, name=species, boxpoints='all', jitter=0.5, whiskerwidth=0.4,
				  marker_size=2, line_width=1.25, boxmean=True)
	box_num_json = pli.to_json(box_num)

	try:
		dist_num = ff.create_distplot([all_intron_num], group_labels = [species])
		dist_num_json = pli.to_json(dist_num)
	except numpy.linalg.LinAlgError:
		dist_num_json = ''

	graphs = {'gff_name': gff_name,
			  'box_1': box_1_json,
			  'dist_1': dist_1_json,
			  'box_all': box_all_json,
			  'dist_all': dist_all_json,
			  'box_tot': box_tot_json,
			  'dist_tot': dist_tot_json,
			  'box_num': box_num_json,
			  'dist_num': dist_num_json 
			  }

	db_connect.close()

	return gene_info, graphs