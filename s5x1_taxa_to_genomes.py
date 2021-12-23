import config
from peewee import *
from ete3 import NCBITaxa


def get_classification(species_name, ext_name, whole_name, other_name = ''):
    ncbi = NCBITaxa()

    correct_names = {'Pythium iwayamai': 'Globisporangium iwayamae',
    'Arthrobotrys oligospora ATCC 24927 (GCA_000225545)': 'Orbilia oligospora ATCC 24927',
    'Aspergillus nomius NRRL 13137 (GCA_001204775)': 'Aspergillus nomiae NRRL 13137',
    'Emergomyces pasteuriana Ep9510 str. UAMH 9510 (GCA_001883825)': 'Emergomyces pasteurianus Ep9510',
    'Emmonsia sp. CAC-2015a str. CBS 136260 (GCA_001660665)': 'Emergomyces africanus',
    'Protomyces lactucaedebilis str. 12-1054 (GCA_002105105)': 'Protomyces lactucae-debilis',
    'Saccharomyces sp. \'boulardii\' str. biocodex (GCA_001298375)': 'Saccharomyces boulardii',
    'Ustilaginomycotina sp. SA 807 (GCA_003144235)': 'Violaceomyces palustris',
    '[Candida] haemulonis str. B11899 (GCA_002926055)': 'Candida haemuloni',
    '[Candida] pseudohaemulonis str. B12108 (GCA_003013735)': '[Candida] pseudohaemulonii'}

    if whole_name in correct_names.keys():
        species_name = correct_names[whole_name]

    try:
        taxid = list(ncbi.get_name_translator([species_name]).values())[0][0]
    except IndexError:
        try:
            taxid = list(ncbi.get_name_translator([ext_name]).values())[0][0]
        except IndexError:
            try:
                taxid = list(ncbi.get_name_translator([other_name]).values())[0][0]
            except IndexError:
                msg = f'Something went wrong with taxonomy for species: {species_name}, {ext_name}, {other_name}'
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

    class Taxonomy(Model):
        gff_name = ForeignKeyField(Species, backref='taxonomy', primary_key = True)
        organism_type = CharField(default = 'Unclassified') 
        superkingdom = CharField(default = 'Unclassified')
        clade = CharField(default = 'Unclassified')
        kingdom = CharField(default = 'Unclassified')
        subkingdom =  CharField(default = 'Unclassified')
        phylum = CharField(default = 'Unclassified')
        subphylum = CharField(default = 'Unclassified')
        superclass = CharField(default = 'Unclassified')
        class_ = CharField(default = 'Unclassified')
        subclass = CharField(default = 'Unclassified')
        infraclass = CharField(default = 'Unclassified')
        cohort = CharField(default = 'Unclassified')
        superorder = CharField(default = 'Unclassified')
        order_ = CharField(default = 'Unclassified')
        infraorder = CharField(default = 'Unclassified')
        suborder = CharField(default = 'Unclassified')
        parvorder = CharField(default = 'Unclassified')
        tribe = CharField(default = 'Unclassified')
        subtribe = CharField(default = 'Unclassified')
        section = CharField(default = 'Unclassified')
        superfamily = CharField(default = 'Unclassified')
        family = CharField(default = 'Unclassified')
        subfamily =  CharField(default = 'Unclassified')
        genus = CharField(default = 'Unclassified')
        subgenus = CharField(default = 'Unclassified')
        species = CharField(default = 'Unclassified')

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

    species = [{'gff_name': species[0], 'name': species[1]} for species in cur.fetchall()]

    taxa = []

    for element in species:

        spc = element['gff_name'].split('.')[0]

        if spc[0] == '_':
            spc = spc[1:]

        spc = spc.split('_')[0] + ' ' + spc.split('_')[1]
        spc = spc[0].upper() + spc[1:]

        sp = element['name']
        sp_alt = ''

        if sp[0:9] == '[Candida]':
            sp = 'Candida' + sp[9:]

        sp_fragm = sp.split(' ')

        if sp_fragm[-1][0:4] == '(GCA':
            sp_fragm = sp_fragm[:-1]
            sp = sp.split(' (GCA')[0]

        if (len(sp_fragm) == 2) or (len(sp_fragm) == 3):
            pass
        elif len(sp_fragm) > 2 and sp_fragm[1] == 'sp.':
            sp = sp_fragm[0] + ' ' + sp_fragm[1] + ' ' + sp_fragm[2]
            if len(sp_fragm) > 3:
                sp_alt = sp_fragm[0] + ' ' + sp_fragm[1] + ' ' + sp_fragm[2] + ' ' + sp_fragm[3]
        elif len(sp_fragm) > 3 and sp_fragm[2] == 'str.':
            sp = sp_fragm[0] + ' ' + sp_fragm[1] + ' ' + sp_fragm[2] + ' ' + sp_fragm[3]
        elif len(sp_fragm) > 3:
            sp = sp_fragm[0] + ' ' + sp_fragm[1] + ' ' + sp_fragm[2] + ' ' + sp_fragm[3]

        try:
            a = get_classification(spc, sp, element['name'], sp_alt)
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

    #Taxonomy.insert_many(taxa).execute()

    with db.atomic():

        print('Inserting Species Stats Info into DB')
        for batch in chunked(taxa, 100):
            Taxonomy.insert_many(batch).execute()

    db.close()