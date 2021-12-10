import config
from peewee import *
from ete3 import NCBITaxa


def get_classification(species_name):
    ncbi = NCBITaxa()
    try:
        taxid = list(ncbi.get_name_translator([species_name]).values())[0][0]
    except IndexError:
        msg = f'Something went wrong with taxonomy for species: {species_name}'
        print(msg)
        raise RuntimeError(msg)

    lineage = ncbi.get_lineage(taxid)
    lineage_names = ncbi.get_taxid_translator(lineage)

    taxonomy = {}
    for taxid in lineage:
        rank = list(ncbi.get_rank([taxid]).values())[0]
        name = lineage_names[taxid]
        taxonomy[rank] = name
    return taxonomy

### -------------------------------------------------------------------------------

if __name__ == '__main__':

    db = SqliteDatabase(config.GENERAL_DB_DIR / 'GenomesDb.sql') 
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
        trans_num = BigIntegerField()
        exon_num = BigIntegerField()
        gene_dens = DecimalField()
        intron_gene_dens = DecimalField()
        avg_gene_len = DecimalField()
        avg_intron_gene_len = DecimalField()
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
        trans_num = BigIntegerField()
        exon_num = BigIntegerField()
        gene_dens = DecimalField()
        intron_gene_dens = DecimalField()
        avg_gene_len = DecimalField()
        avg_intron_gene_len = DecimalField()
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

    class Taxonomy(Model):
        gff_name = ForeignKeyField(Species, backref='taxonomy', primary_key = True)
        organism_type = CharField(default = '') 
        superkingdom = CharField(default = '')
        clade = CharField(default = '')
        kingdom = CharField(default = '')
        subkingdom =  CharField(default = '')
        phylum = CharField(default = '')
        subphylum = CharField(default = '')
        superclass = CharField(default = '')
        class_ = CharField(default = '')
        subclass = CharField(default = '')
        infraclass = CharField(default = '')
        cohort = CharField(default = '')
        superorder = CharField(default = '')
        order_ = CharField(default = '')
        infraorder = CharField(default = '')
        suborder = CharField(default = '')
        parvorder = CharField(default = '')
        tribe = CharField(default = '')
        superfamily = CharField(default = '')
        family = CharField(default = '')
        subfamily =  CharField(default = '')
        genus = CharField(default = '')
        subgenus = CharField(default = '')
        species = CharField(default = '')

        class Meta:
            database = db 
            table_name = 'taxonomy'

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

    db.bind([Species, Stats, Stats_Prot, Graphs, Graphs_Prot])

    db.create_tables([Taxonomy])

    cur = db.execute_sql('SELECT gff_name, name FROM species')
    #cur = db.execute_sql('SELECT s.gff_name_id, spc.name FROM stats s JOIN species spc ON (s.gff_name_id = spc.gff_name)')

    species = [{'gff_name': species[0], 'name': species[1]} for species in cur.fetchall()]

    taxa = []

    for element in species:

        spc = element['gff_name'].split('.')[0]

        if spc[0] == '_':
            spc = spc[1:]

        spc = spc.split('_')[0] + ' ' + spc.split('_')[1]
        spc = spc[0].upper() + spc[1:]

        try:
            a = get_classification(spc)
        except RuntimeError:
            continue
        
        try:
            a['organism_type'] = a['no rank']
            del a['no rank']
        except KeyError:
            pass

        try:
            a['class_'] = a['class']
            del a['class']
        except KeyError:
            pass

        try:
            a['order_'] = a['order']
            del a['order']
        except KeyError:
            pass

        a['gff_name_id'] = element['gff_name']

        taxa.append(a)

    # for smth in taxa:
    #     print(smth)
    #     Taxonomy.insert(smth).execute()

    Taxonomy.insert_many(taxa).execute()

    # with db.atomic():

    #     print('Inserting Species Stats Info into DB')
    #     for batch in chunked(taxa, 100):
    #         Taxonomy.insert_many(batch).execute()

    db.close()