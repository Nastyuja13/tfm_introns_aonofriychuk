import os
from peewee import *
import config


# Creating names and paths for the preliminar & real Db
def db_names(species_name):

  db_name = species_name + '.sql'
  db_path = config.NEW_DB_DIR / db_name

  db_name_0 = db_name + '0'
  db_path_0 = config.NEW_DB_DIR / db_name_0

  return db_name, db_path, db_name_0, db_path_0


# Db creation
# Saves db as a preliminar file(.sql_0) so it can be renamed
# when the db is really filled by the 'gff_to_db' function
def create_species_db_0(species_name):

    db_name = db_names(species_name)[0]
    db_path = db_names(species_name)[1]
    db_path_0 = db_names(species_name)[3]

    if os.path.isfile(db_path):
      if os.path.getsize(db_path) > 0:
        print(f'The {db_name} database already exists')
        return 'EXISTS'
      else:
        print(f'The {db_name} database already exists, but is empty')
        print(f'The database will be rewritten')
        os.remove(db_path)
    else:
      pass

    if os.path.isfile(db_path_0):
      os.remove(db_path_0)
    else:
      pass

    # Database creation
    db = SqliteDatabase(db_path_0)

    return db


# Global db function with classes and Db creation
def gff_to_db(species_name, db, gene_dict, trans_dict, exon_dict):

  # Database 
  db = db

  # Classes defined for the db tables and extracted gff info
  # Class definition according to the data obtained from gff_parsing.py
  class Gene(Model):
    gene_id = CharField(primary_key = True)
    start = BigIntegerField()
    end = BigIntegerField()
    strand = CharField(max_length = 1)
    biotype = CharField()
    description = CharField(max_length = 350)

    class Meta:
      database = db 
      table_name = 'genes'

  class Transcript(Model):  
    trans_id = CharField(primary_key = True)
    start = BigIntegerField()
    end = BigIntegerField()
    strand = CharField(max_length = 1)
    biotype = CharField()
    gene = ForeignKeyField(Gene, backref='transcripts')

    class Meta:
      database = db 
      table_name = 'transcripts'

  class Exon(Model):  
    exon_id = CharField()
    start = BigIntegerField()
    end = BigIntegerField()
    exon_length = IntegerField()
    strand = CharField(max_length = 1)
    transcript = ForeignKeyField(Transcript, backref='exons')

    class Meta:
      database = db 
      table_name = 'exons'
      primary_key = CompositeKey('exon_id', 'transcript')

  # Connection to the database & table creation
  db.connect()
  db.create_tables([Gene, Transcript, Exon])

  # Fill the database tables as atomic operations
  with db.atomic():

      #print('Inserting genes')
      for batch in chunked(gene_dict, 100):
        Gene.insert_many(batch).execute()

      #print('Inserting transcripts')
      for batch in chunked(trans_dict, 100):
        Transcript.insert_many(batch).execute()

      #print('Inserting exons')
      for batch in chunked(exon_dict, 100):
        Exon.insert_many(batch).execute()

  # Close the database
  db.close()

  # Rename the definitive database
  db_name = db_names(species_name)[0]
  db_path = db_names(species_name)[1]
  db_path_0 = db_names(species_name)[3]

  os.rename(db_path_0, db_path)
  print(f'The {db_name} database was filled successfully')