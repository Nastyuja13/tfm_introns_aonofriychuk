# Import of libraries

import os
from pathlib import Path
import time
import sqlite3

import config
from s3x2_gff_parsing import parse_gff
import s3x3_db_tables_creation as db_cr


if __name__ == '__main__':

    db_connect = sqlite3.connect(config.GENERAL_DB_DIR /'GenomesDb.sql') # 'GenomesDb.sql'
    cur = db_connect.cursor()

    cur.execute('SELECT gff_file FROM species')
    gff_files = [file[0] for file in cur.fetchall()]

    base_path = config.NEW_DOWNLOAD_DIR

    for gff_file in gff_files:

        print(f'\n--- Processing {gff_file} ---')

        gff_path = base_path / gff_file

        if not os.path.isfile(gff_path):

            err = f'Error: {gff_file} is not available'
            print(err)
            with open(config.ERRORLOG_DIR /'ErrorLogGeneDb.txt','a') as errorlog:
                errorlog.write(err + '\n')
            errorlog.close()

            continue

        species_name = gff_file.split('.gff3.gz')[0]

        start_time = time.time()

        db = db_cr.create_species_db_0(species_name)

        if db == 'EXISTS':
            continue
        else:
            pass

        parsed_gff = parse_gff(gff_path)

        if parsed_gff == 'BAD-PARSING':
            continue
        else:
            pass

        gene_dict = parsed_gff[0]
        ### check if genes fail to be unique ###
        #print(len(gene_dict))
        #aaa = []
        #for gn in gene_dict:
            #a = gn['gene_id']
            #if a in aaa:
                #print(a)
                #print(gn)
            #aaa.append(a)

        #print(str(len(set(aaa))))
        #print(aaa[1:5])

        trans_dict = parsed_gff[1]
        ### check if transcripts fail to be unique ###
        #print('How many transcripts: ' + str(len(trans_dict)))

        #aaa = []
        #for tr in trans_dict:
            #a = tr['trans_id']
            #if a in aaa:
                #print(tr)
            #aaa.append(a)

        #print(str(len(aaa)))
        #print(aaa[1:5])

        exon_dict = parsed_gff[2]

        db_cr.gff_to_db(species_name, db, gene_dict, trans_dict, exon_dict)

        final_time = round(time.time() - start_time, 3)

        print(f"It took {final_time} seconds for {gff_file} DB creation")