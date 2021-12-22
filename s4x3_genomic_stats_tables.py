# DB creation for stats & graphs
import config
from peewee import *

def create_stat_graph_tables(genomes_db, stats, stats_prot, graphs, graphs_prot):

	db = SqliteDatabase(config.GENERAL_DB_DIR / genomes_db)
	db.connect()

	class Species(Model):
		name = CharField()
		species = CharField() 
		common_name = CharField() 
		species_type = CharField()
		release = IntegerField()
		genome_length = BigIntegerField()
		gff_name = CharField(primary_key = True)
		gff_link = CharField()
		gff_file = CharField()

		class Meta:
			database = db 
			table_name = 'species'

	class Stats(Model):
		gff_name = ForeignKeyField(Species, backref='stats', primary_key = True)
		gene_num = BigIntegerField()
		genes_with_introns_num = BigIntegerField()
		trans_num = BigIntegerField()
		exon_num = BigIntegerField()
		gene_dens = DecimalField()
		intron_gene_dens = DecimalField()
		avg_gene_len = DecimalField()
		avg_intron_gene_len = DecimalField()
		avg_exon_len = DecimalField()
		avg_exon_len_in_int_genes = DecimalField()
		avg_trans_per_gene = DecimalField()
		avg_exon_per_trans = DecimalField()
		avg_exon_per_gene = DecimalField()
		avg_intron_num_per_gene = DecimalField()
		avg_intron_num_per_gene_with_introns = DecimalField()
		avg_intron_len = DecimalField()
		avg_first_intron_len = DecimalField()
		avg_total_intron_len = DecimalField()

		class Meta:
			database = db 
			table_name = 'stats'


	class Stats_Prot(Model):
		gff_name = ForeignKeyField(Species, backref='stats_prot', primary_key = True)
		gene_num = BigIntegerField()
		genes_with_introns_num = BigIntegerField()
		trans_num = BigIntegerField()
		exon_num = BigIntegerField()
		gene_dens = DecimalField()
		intron_gene_dens = DecimalField()
		avg_gene_len = DecimalField()
		avg_intron_gene_len = DecimalField()
		avg_exon_len = DecimalField()
		avg_exon_len_in_int_genes = DecimalField()
		avg_trans_per_gene = DecimalField()
		avg_exon_per_trans = DecimalField()
		avg_exon_per_gene = DecimalField()
		avg_intron_num_per_gene = DecimalField()
		avg_intron_num_per_gene_with_introns = DecimalField()
		avg_intron_len = DecimalField()
		avg_first_intron_len = DecimalField()
		avg_total_intron_len = DecimalField()

		class Meta:
			database = db 
			table_name = 'stats_prot'

	class Graphs(Model):
		gff_name = ForeignKeyField(Species, backref='graphs', primary_key = True)
		box_1 = TextField()
		dist_1 = TextField()
		box_all = TextField()
		dist_all = TextField()
		box_tot = TextField()
		dist_tot = TextField()
		box_num = TextField()
		dist_num = TextField()

		class Meta:
			database = db 
			table_name = 'graphs'

	class Graphs_Prot(Model):
		gff_name = ForeignKeyField(Species, backref='graphs_prot', primary_key = True)
		box_1 = TextField()
		dist_1 = TextField()
		box_all = TextField()
		dist_all = TextField()
		box_tot = TextField()
		dist_tot = TextField()
		box_num = TextField()
		dist_num = TextField()

		class Meta:
			database = db 
			table_name = 'graphs_prot'

	db.bind([Species])

	db.create_tables([Stats, Stats_Prot, Graphs, Graphs_Prot])


	with db.atomic():

		print('Inserting Species Stats Info into DB')
		for batch in chunked(stats, 100):
			Stats.insert_many(batch).execute()

	with db.atomic():

		print('Inserting Species Prot Stats Info into DB')
		for batch in chunked(stats_prot, 100):
			Stats_Prot.insert_many(batch).execute()

	with db.atomic():
		print('Inserting Species Graphs Info into DB')
		for batch in chunked(graphs, 100):
			Graphs.insert_many(batch).execute()

	with db.atomic():

		print('Inserting Species Prot Graphs Info into DB')
		for batch in chunked(graphs_prot, 100):
			Graphs_Prot.insert_many(batch).execute()

	print('Done')

	db.close()