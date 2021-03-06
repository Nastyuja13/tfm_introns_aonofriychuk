import config
import sqlite3
import time
import pandas as pd
import s4x2_genome_stat_funcs as gs
import s4x3_genomic_stats_tables as gst


if __name__ == '__main__':

	genomes_db = 'GenomesDb.sql'

	# Connect to genomes DB and obtain the list of all species

	db_connect = sqlite3.connect(config.GENERAL_DB_DIR / genomes_db)
	cur = db_connect.cursor()

	cur.execute('SELECT gff_name, species, species_type, genome_length FROM species')

	gff3s = [{'gff_name': gff3[0], 'sql': gff3[0] + '.sql', 'species': gff3[1], 'species_type': gff3[2], 'genome_length': gff3[3]} for gff3 in cur.fetchall()]

	db_connect.close()

	# Calculate stats and graphs for each species in the list, for all & only protein-coding genes

	statss = []
	statss_prot = []
	graphs_introns = []
	graphs_introns_prot = []

	## For each genome annotation (each sql file)
	for gff in gff3s:

		start_time = time.time()

		print('###')
		print('Calculating stats for: ' + gff['sql'] + ', ' + gff['species_type'])

		## Select all genes and get their stats

		gene_info, graphs = gs.get_gene_stats(gff['gff_name'], gff['species'], gff['genome_length'])
		statss.append(gene_info)
		graphs_introns.append(graphs)

		## Select only protein-coding genes and get their stats

		prot_gene_info, graphs_prot = gs.get_gene_stats(gff['gff_name'], gff['species'], gff['genome_length'], 'protein_coding')
		statss_prot.append(prot_gene_info)
		graphs_introns_prot.append(graphs_prot)

		final_time = round(time.time() - start_time, 3)
		print(f"It took {final_time} seconds for {gff['gff_name']} stats calculus")

	# Insert stats and graphs into the database

	gst.create_stat_graph_tables(genomes_db, statss, statss_prot, graphs_introns, graphs_introns_prot)