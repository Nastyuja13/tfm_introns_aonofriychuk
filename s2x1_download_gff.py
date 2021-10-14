import os
import sqlite3
import requests

import config

def obtain_gff_link_from_db(genome):

    db_connect = sqlite3.connect(genome) # 'GenomesDb.sql'
    cur = db_connect.cursor()

    cur.execute('SELECT gff_link FROM species')
    links = [link[0] for link in cur.fetchall()]

    return links


def download_gff(url):

    # http://ftp.ebi.ac.uk/ensemblgenomes/pub/release-51/metazoa/gff3/caenorhabditis_elegans/Caenorhabditis_elegans.WBcel235.51.gff3.gz
    filename = url.split('/')[-1]
    print(f'### Processing {filename} ###')
    gff3_path = config.NEW_DOWNLOAD_DIR / filename

    file_exists = os.path.isfile(gff3_path)

    if file_exists:
        file_size = os.path.getsize(gff3_path)
    else:
        file_size = -1

    if ((file_exists == True) & (file_size > 0)):
        print(f'Skip: {filename} already exists')
    else:
        print(f'Downloading {filename}')
        if file_size == 0:
            print(f'Redownload: {filename} already exists but is empty')
            os.remove(gff3_path)

        try:
            gff3 = requests.get(url, stream = True)

            filename_0 = filename + '_0'

            gff3_path_0 = config.NEW_DOWNLOAD_DIR / filename_0

            if os.path.isfile(gff3_path_0):
                os.remove(gff3_path_0)

            with open(gff3_path_0, 'wb') as gz_file:

                for chunk in gff3.raw.stream(1024, decode_content=True):
                    gz_file.write(chunk)

            gz_file.close()

            os.rename(gff3_path_0, gff3_path)

            if os.path.isfile(gff3_path) == True:
                print('Successfull download')
            else:
                with open(config.ERRORLOG_DIR /'ErrorLogGffDownload.txt', 'a') as errorlog:
                    errorlog.write(f'File {filename} failed to be downloaded\n')
                errorlog.close()
                print('Download failed')
                
        except requests.exceptions.ConnectionError:
            with open(config.ERRORLOG_DIR /'ErrorLogGffDownload.txt', 'a') as errorlog:
                    errorlog.write(f'File {filename} failed to be downloaded\n')
            errorlog.close()
            print(f'Error downloading {filename}')


if __name__ == '__main__':

    links = obtain_gff_link_from_db(config.GENERAL_DB_DIR / 'GenomesDb.sql')

    for link in links:
        download_gff(link)