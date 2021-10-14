from peewee import *
import config

# Definition of the specific database
def create_genomes_db(db_name = 'GenomesDb'):

    db_name = db_name + '.sql'
    db_path = config.GENERAL_DB_DIR / db_name
    db = SqliteDatabase(db_path)

    return db


# Global db function with classes
def species_info_to_db(speciess):

  # Database definition
  db = create_genomes_db()

  # Classes defined for the db tables and the species info
  class Species(Model):
    name = CharField()
    species = CharField() 
    common_name = CharField() 
    species_type = CharField()
    gff_link = CharField()
    gff_file = CharField()

    class Meta:
      database = db 
      table_name = 'species'

  #class Stats(Model):  
    

    #class Meta:
      #database = db 
      #table_name = 'stats'


  # Connection to the database & table creation
  db.connect()
  db.create_tables([Species])

  # Fill the database tables as atomic operations
  with db.atomic():

      print('Inserting Species Info into DB')
      for batch in chunked(speciess, 100):
        Species.insert_many(batch).execute()

  # Close the database
  db.close()

  print('Done')