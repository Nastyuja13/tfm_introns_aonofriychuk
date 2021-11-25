import config
from peewee import *
from ete3 import NCBITaxa


def get_classification(species_name):
    ncbi = NCBITaxa()
    try:
        taxid = list(ncbi.get_name_translator([species_name]).values())[0][0]
    except IndexError:
        msg = f'Something went wrong with taxonomy for species: {species_name}'
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

    class Taxonomy(Model):
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
        tribe = CharField(default = '')
        superfamily = CharField(default = '')
        family = CharField(default = '')
        subfamily =  CharField(default = '')
        genus = CharField(default = '')
        species = ForeignKeyField(Species, backref='species')

        class Meta:
            database = db 
            table_name = 'taxonomy'

    db.bind([Species, Stats])

    db.create_tables([Taxonomy])

    cur = db.execute_sql('SELECT gff_name_id FROM stats')

    species0 = [gff_name[0].split('.')[0] for gff_name in cur.fetchall()]
    species = []

    for s in species0:
        if s[0] == '_':
            s = s[1:]

        s = s.split('_')[0] + ' ' + s.split('_')[1]
        s = s[0].upper() + s[1:]

        species.append(s)

    print(species)
    taxa = []

    for spc in species:

        a = get_classification(spc)
        a['organism_type'] = a['no rank']
        del a['no rank']
        a['class_'] = a['class']
        del a['class']
        a['order_'] = a['order']
        del a['order']

        taxa.append(a)

    print(taxa)

    Taxonomy.insert_many(taxa).execute()

    # with db.atomic():

    #     print('Inserting Species Stats Info into DB')
    #     for batch in chunked(taxa, 100):
    #         Taxonomy.insert_many(batch).execute()

    db.close()