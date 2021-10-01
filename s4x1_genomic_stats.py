import config
import sqlite3
import random

def _det_strand(exons):

	prev_strand = ''

	for exon in exons:
		strand = exon[strand]
		if strand == prev_strand:
			continue
		else:
			

	return strand




db_connect = sqlite3.connect(config.NEW_DB_DIR / 'Mus_musculus.GRCm39.104.sql') 
cur = db_connect.cursor()

cur.execute('SELECT gene_id FROM genes')
genes = [gene[0] for gene in cur.fetchall()]

print('Number of genes:' + str(len(genes)))

cur.execute('SELECT trans_id FROM transcripts')
ts = [t[0] for t in cur.fetchall()]

print('Number of transcripts:' + str(len(ts)))

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



    #exon_positions = res['exon_positions']

    #exon_positions = sorted(exon_positions, key=lambda x: x[0])
    #intron_len = 0
    #for exon_a, exon_b in zip(exon_positions[:-1], exon_positions[1:]):
        #intron_len += abs(exon_b[0] - exon_a[1])

	if i == 2:
		break
