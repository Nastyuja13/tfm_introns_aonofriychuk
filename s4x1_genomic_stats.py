import config
import sqlite3
import random
import plot
import requests
from bs4 import BeautifulSoup
import re
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

def get_golden_path_len(gff_name, species_type):
	#http://metazoa.ensembl.org/Apis_mellifera/Info/Annotation/
	#http://www.ensembl.org/Felis_catus/Info/Index
	#http://fungi.ensembl.org/Saccharomyces_cerevisiae/Info/Annotation/#assembly
	#http://protists.ensembl.org/Plasmodium_falciparum/Info/Annotation/#assembly
	#http://plants.ensembl.org/Arabidopsis_thaliana/Info/Annotation/#assembly
	spc = gff_name.split('.')[0]
	
	if species_type != 'main':
		html_path = "http://{a}.ensembl.org/{b}/Info/Annotation/".format(a=species_type, b=spc)
	else:
		html_path = "http://www.ensembl.org/{b}/Info/Annotation/".format(b=spc)

	html = requests.get(html_path).text

	#soup = BeautifulSoup(html, 'html.parser')

	match = re.search('<b>Golden Path Length</b></td>[^>]+>(?P<genome_size>[^<]+)</td>', html, re.I)
	#<b>Golden Path Length</b></td><td style="width:70%;text-align:left">100,286,401</td>

	if not match:

		match = None
		#raise RuntimeError('No golden path found')

	return int(match['genome_size'].replace(',', ''))

###

# data = {}

# db_connect = sqlite3.connect(config.NEW_DB_DIR / 'Apis_mellifera.Amel_HAv3.1.51.sql') 
# #db_connect = sqlite3.connect(config.NEW_DB_DIR / '_candida_auris_gca_002775015.Cand_auris_B11221_V1.51.sql')
# #db_connect = sqlite3.connect(config.NEW_DB_DIR / 'Felis_catus.Felis_catus_9.0.104.sql') 
# cur = db_connect.cursor()

# cur.execute('SELECT gene_id, start, end FROM genes WHERE biotype LIKE "protein_coding"')

# genes_lens = {gene[0]: {'start': gene[1], 'end': gene[2]} for gene in cur.fetchall()}

# genes = genes_lens.keys()

# print('Number of genes: ' + str(len(genes)))
# print('Avg gene len: ' + str(avg_gene_len(genes_lens)))

# cur.execute('SELECT trans_id FROM transcripts')
# ts = [t[0] for t in cur.fetchall()]

# print('Number of transcripts: ' + str(len(ts)))

# print(avg_trans_per_gene(ts, genes))

# cur.execute('SELECT exon_id FROM exons')
# ex = [e[0] for e in cur.fetchall()]

# print('Number of exons: ' + str(len(ex)))

# print(avg_exon_per_trans(ex, ts))
# print(avg_exon_per_gene(ex, genes))

# #i = 0

# all_introns = []
# all_tot_introns = []
# all_first_introns = []

# for gene in genes:

# 	cur.execute('SELECT trans_id FROM transcripts WHERE gene_id = ?', (gene,))
# 	transcripts = [trans[0] for trans in cur.fetchall()]

# 	transcript_id = random.choice(transcripts)

# 	cur.execute('SELECT exon_id, start, end, strand FROM exons WHERE transcript_id = ?', (transcript_id,))
# 	exons = {exon[0]: {'start': exon[1], 'end': exon[2], 'strand': exon[3]} for exon in cur.fetchall()}

# 	ex_len = exon_len(exons)
# 	tot_ex_len = total_exon_len(ex_len)
# 	if len(ex_len) > 1:
# 		int_len = intron_len(exons)
# 		tot_int_len = total_intron_len(intron_len(exons))

# 		all_introns = all_introns + int_len
# 		all_tot_introns.append(tot_int_len)
# 		all_first_introns.append(int_len[0])
# 	else:
# 		pass

# all_first_introns = sorted(all_first_introns)

# print('Avg introns per gene: ' + str(len(all_introns)/len(genes)))

# print('Avg of all intron lengths: ' + str(sum(all_introns)/len(all_introns)))
# print('Avg of total intron lengths: ' + str(sum(all_tot_introns)/(len(all_tot_introns))))
# print('Avg of first intron lengths: ' + str(sum(all_first_introns)/(len(all_first_introns))))

# db_connect.close()

# data['First_int_len'] = all_first_introns
# data['species'] = ['Apis_mel' for element in range(0, len(all_first_introns))]

# 	#i = i + 1

# 	#print('### Gene: ' + gene)
# 	#print('Len: ' + str(genes_lens[gene]['end'] - genes_lens[gene]['start'] + 1))
# 	#print('Start: ' + str(genes_lens[gene]['start']))
# 	#print('End: ' + str(genes_lens[gene]['end']))

# 	#cur.execute('SELECT trans_id FROM transcripts WHERE gene_id = ?', (gene,))
# 	#transcripts = [trans[0] for trans in cur.fetchall()]
# 	#print(transcripts)

# 	#transcript_id = random.choice(transcripts)
# 	#print('# Transcript: ' + transcript_id)

# 	#cur.execute('SELECT exon_id, start, end, strand FROM exons WHERE transcript_id = ?', (transcript_id,))
# 	#exons = {exon[0]: {'start': exon[1], 'end': exon[2], 'strand': exon[3]} for exon in cur.fetchall()}

# 	#print(exon_len(exons))
# 	#print(total_exon_len(exon_len(exons)))
# 	#print(exons)
# 	#if len(exons) > 1:
# 		#print(intron_len(exons))
# 		#print(total_intron_len(intron_len(exons)))

# 	#if i == 2:
# 		#db_connect.close()
# 		#break

# ###

# data2 = {}

# db_connect = sqlite3.connect(config.NEW_DB_DIR / 'Felis_catus.Felis_catus_9.0.104.sql')
# #db_connect = sqlite3.connect(config.NEW_DB_DIR / 'Apis_mellifera.Amel_HAv3.1.51.sql')  
# #db_connect = sqlite3.connect(config.NEW_DB_DIR / '_candida_auris_gca_002775015.Cand_auris_B11221_V1.51.sql')
# cur = db_connect.cursor()

# cur.execute('SELECT gene_id, start, end FROM genes WHERE biotype LIKE "protein_coding"')

# genes_lens = {gene[0]: {'start': gene[1], 'end': gene[2]} for gene in cur.fetchall()}

# genes = genes_lens.keys()

# print('Number of genes: ' + str(len(genes)))
# print('Avg gene len: ' + str(avg_gene_len(genes_lens)))

# cur.execute('SELECT trans_id FROM transcripts')
# ts = [t[0] for t in cur.fetchall()]

# print('Number of transcripts: ' + str(len(ts)))
# print('Avg transcripts per gene: ' + str(avg_trans_per_gene(ts, genes)))

# cur.execute('SELECT exon_id FROM exons')
# ex = [ex[0] for ex in cur.fetchall()]

# print('Number of exons: ' + str(len(ex)))

# print('Avg exons per transcripts: ' + str(avg_exon_per_trans(ex, ts)))
# print('Avg exons per gene: ' + str(avg_exon_per_gene(ex, genes)))

# all_introns = []
# all_tot_introns = []
# all_first_introns = []

# for gene in genes:

# 	cur.execute('SELECT trans_id FROM transcripts WHERE gene_id = ?', (gene,))
# 	transcripts = [trans[0] for trans in cur.fetchall()]

# 	transcript_id = random.choice(transcripts)

# 	cur.execute('SELECT exon_id, start, end, strand FROM exons WHERE transcript_id = ?', (transcript_id,))
# 	exons = {exon[0]: {'start': exon[1], 'end': exon[2], 'strand': exon[3]} for exon in cur.fetchall()}

# 	ex_len = exon_len(exons)
# 	tot_ex_len = total_exon_len(ex_len)
# 	if len(ex_len) > 1:
# 		int_len = intron_len(exons)
# 		tot_int_len = total_intron_len(intron_len(exons))

# 		all_introns = all_introns + int_len
# 		all_tot_introns.append(tot_int_len)
# 		all_first_introns.append(int_len[0])
# 	else:
# 		pass

# all_first_introns = sorted(all_first_introns)

# print('Avg introns per gene: ' + str(len(all_introns)/len(genes)))

# print('Avg of all intron lengths: ' + str(sum(all_introns)/len(all_introns)))
# print('Avg of total intron lengths: ' + str(sum(all_tot_introns)/(len(all_tot_introns))))
# print('Avg of first intron lengths: ' + str(sum(all_first_introns)/(len(all_first_introns))))

# db_connect.close()

# data2['First_int_len'] = all_first_introns
# data2['species'] = ['Felis_catus' for element in range(0, len(all_first_introns))]

# df1 = pd.DataFrame(data=data)
# df2 = pd.DataFrame(data=data2)

# df = pd.concat([df1, df2])

# #sns.set_theme(style="whitegrid")
# #ax = sns.boxplot(x=df['species'], y=df['First_int_len'])

# #fig = ax.get_figure()
# #fig.savefig("output.png")
# #plot_intron_size_distrib(all_first_introns, "distrib.png")

# ax2 = sns.displot(df1[:5000], x="First_int_len")
# ax2.savefig("output2.png")

# ax3 = sns.displot(df2[:14000], x="First_int_len")
# ax3.savefig("output3.png")

# #import plotly.graph_objects as go

# print(len(df1['First_int_len']))
# print(len(df2['First_int_len']))

#for i in [500, 1000, 2500, 5000, 6000, 7000, 8000]:

	#df3 = pd.concat([df1[:i], df2[:i]])

	#fig = go.Figure()
	#fig.add_trace(go.Box(
		#x=df3['species'],
    	#y=df3['First_int_len'],
    	#name='Mean & SD',
    	#marker_color='royalblue',
    	#boxmean='sd' # represent mean and standard deviation
	#))

	#fig.show()

db_connect = sqlite3.connect(config.GENERAL_DB_DIR / 'xxGenomesDb.sql') 
cur = db_connect.cursor()#

#cur.execute('SELECT gff_name, species_type, gff_file FROM species WHERE gff_name LIKE "_candida_auris_gca_002775015.Cand_auris_B11221_V1.51"')
#cur.execute('SELECT gff_name, species_type, gff_file FROM species WHERE gff_name LIKE "Felis_catus.Felis_catus_9.0.104"')
cur.execute('SELECT gff_name, species_type, gff_file FROM species WHERE gff_name LIKE "Apis_mellifera.Amel_HAv3.1.51"')

gff3s = [{'gff_name': gff3[0], 'sql': gff3[2][:-8] + '.sql', 'species_type': gff3[1]} for gff3 in cur.fetchall()]#

db_connect.close()

from peewee import *

j = 0

statss = []#

for gff in gff3s:#

	print(gff)#

	db_connect = sqlite3.connect(config.NEW_DB_DIR / gff['sql']) 
	cur = db_connect.cursor()

	cur.execute('SELECT gene_id, start, end FROM genes')
	genes_lens = {gene[0]: {'start': gene[1], 'end': gene[2]} for gene in cur.fetchall()}
	genes = genes_lens.keys()
	print('Number of genes:' + str(len(genes)))
	print('Avg gene len:' + str(avg_gene_len(genes_lens)))

	cur.execute('SELECT trans_id FROM transcripts')
	ts = [t[0] for t in cur.fetchall()]
	print('Number of transcripts:' + str(len(ts)))

	cur.execute('SELECT exon_id FROM exons')
	ex = [e[0] for e in cur.fetchall()]

	print('Number of exons:' + str(len(ex)))

	print('Golden path length: ' + str(get_golden_path_len(gff['gff_name'], gff['species_type'])))

	gene_info = {'gff_name': gff['gff_name'],
	             'gene_num': len(genes),
                 'trans_num': len(ts),
                 'exon_num': len(ex),
                 'avg_gene_len': avg_gene_len(genes_lens),
                 'avg_trans_per_gene': avg_trans_per_gene(ts, genes),
                 'avg_exon_per_trans': avg_exon_per_trans(ex, ts),
                 'avg_exon_per_gene': avg_exon_per_gene(ex, genes),
                 'genome_length': get_golden_path_len(gff['gff_name'], gff['species_type'])
                 #'avg_exon_len_per_gene': BigIntegerField(),
                 #'avg_exon_len_per_trans': BigIntegerField(),
                 #'avg_intron_len_per_gene': BigIntegerField(),
                 #'avg_intron_len_per_trans': BigIntegerField()
                 }

	statss.append(gene_info)

	db_connect.close()
#	j = j + 1#

#	if j == 5:
#		break#

#################################

db = SqliteDatabase(config.GENERAL_DB_DIR / 'GenomesDb2.sql')
db.connect()

class Species(Model):
	name = CharField()
	species = CharField() 
	common_name = CharField() 
	species_type = CharField()
	release = IntegerField()
	gff_name = CharField(primary_key = True)
	gff_link = CharField()
	gff_file = CharField()

	class Meta:
		database = db 
		table_name = 'species'

class Stats(Model):
	gff_name = ForeignKeyField(Species, backref='stats', primary_key = True)
	#species = CharField(primary_key = True)
	genome_length = BigIntegerField()
	gene_num = BigIntegerField()
	trans_num = BigIntegerField()
	exon_num = BigIntegerField()
	avg_gene_len = BigIntegerField()
	avg_trans_per_gene = BigIntegerField()
	avg_exon_per_trans = BigIntegerField()
	avg_exon_per_gene = BigIntegerField()
	#avg_exon_len_per_gene = BigIntegerField()
	#avg_exon_len_per_trans = BigIntegerField()
	#avg_intron_len_per_gene = BigIntegerField()
	#avg_intron_len_per_trans = BigIntegerField()

	class Meta:
		database = db 
		table_name = 'stats'

db.bind([Species])

db.create_tables([Stats])

with db.atomic():

    print('Inserting Species Stats Info into DB')
    for batch in chunked(statss, 100):
    	Stats.insert_many(batch).execute()

db.close()