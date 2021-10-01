# Import of libraries

import os
from pathlib import Path
import time
import sqlite3

import config
from s3x2_gff_parsing import parse_gff
import s3x3_db_tables_creation as db_cr


if __name__ == '__main__':

    db_connect = sqlite3.connect('GenomesDb.sql') # 'GenomesDb.sql'
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
            with open('ErrorLogGeneDb.txt','a') as errorlog:
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
        trans_dict = parsed_gff[1]
        exon_dict = parsed_gff[2]

        db_cr.gff_to_db(species_name, db, gene_dict, trans_dict, exon_dict)

        final_time = round(time.time() - start_time, 3)

        print(f"It took {final_time} seconds for {gff_file} DB creation")